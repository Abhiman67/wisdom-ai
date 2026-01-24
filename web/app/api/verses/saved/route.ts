import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const supabase = createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    if (authError || !user) {
      return NextResponse.json({ saved_verses: [] })
    }

    const { data, error } = await supabase
      .from('saved_verses')
      .select('*')
      .eq('user_id', user.id)
      .order('saved_at', { ascending: false })

    if (error) {
      console.error('Error fetching saved verses:', error)
      return NextResponse.json({ saved_verses: [] })
    }

    return NextResponse.json({
      saved_verses: data.map(v => ({
        id: v.id,
        text: v.verse_text,
        source: v.verse_source,
        reflection: v.reflection,
        saved_at: v.saved_at,
      })),
    })
  } catch (error) {
    console.error('Saved verses error:', error)
    return NextResponse.json({ saved_verses: [] })
  }
}

export async function POST(request: Request) {
  try {
    const supabase = createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    if (authError || !user) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
    }

    const { text, source, reflection } = await request.json()

    if (!text || !source) {
      return NextResponse.json(
        { error: 'Verse text and source are required' },
        { status: 400 }
      )
    }

    // Check if already saved
    const { data: existing } = await supabase
      .from('saved_verses')
      .select('id')
      .eq('user_id', user.id)
      .eq('verse_text', text)
      .eq('verse_source', source)
      .single()

    if (existing) {
      return NextResponse.json({ message: 'Verse already saved', id: existing.id })
    }

    const { data, error } = await supabase
      .from('saved_verses')
      .insert({
        user_id: user.id,
        verse_text: text,
        verse_source: source,
        reflection: reflection || null,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 400 })
    }

    return NextResponse.json({
      message: 'Verse saved successfully',
      id: data.id,
    })
  } catch (error) {
    console.error('Save verse error:', error)
    return NextResponse.json(
      { error: 'Failed to save verse' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: Request) {
  try {
    const supabase = createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    if (authError || !user) {
      return NextResponse.json({ error: 'Not authenticated' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')

    if (!id) {
      return NextResponse.json({ error: 'Verse ID is required' }, { status: 400 })
    }

    const { error } = await supabase
      .from('saved_verses')
      .delete()
      .eq('id', id)
      .eq('user_id', user.id)

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 400 })
    }

    return NextResponse.json({ message: 'Verse removed successfully' })
  } catch (error) {
    console.error('Delete verse error:', error)
    return NextResponse.json(
      { error: 'Failed to delete verse' },
      { status: 500 }
    )
  }
}
