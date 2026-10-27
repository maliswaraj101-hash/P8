'use client'

import React, { useState } from 'react'
import Image from 'next/image'
import ReactMarkdown from 'react-markdown'
import { signIn, signOut, useSession } from 'next-auth/react'
import { Sparkles, Search, BookOpen, Image as ImageIcon, Tag, Loader2 } from 'lucide-react'

export type BlogSection = [number, string];

export type BlogTask = {
  id: number;
  title: string;
  goal: string;
  bullets: string[];
  target_words: number;
  tags: string[];
  requires_research: boolean;
  requires_citations: boolean;
  requires_code: boolean;
};

export type BlogPlan = {
  blog_title: string;
  audience: string;
  tone: string;
  blog_kind: string;
  constraints: string[];
  tasks: BlogTask[];
};

export type BlogResponse = {
  response: {
    topic: string;
    mode: string;
    needs_research: boolean;
    queries: string[];
    evidence: any[];
    plan: BlogPlan;
    as_of: string;
    recency_days: number;
    sections: BlogSection[];
  }
}

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:4000'

const App: React.FC = () => {
  const { data: session, status } = useSession()
  const [topic, setTopic] = useState('')
  const [blogKind, setBlogKind] = useState('Professional')
  const [loading, setLoading] = useState(false)
  const [blogData, setBlogData] = useState<BlogResponse['response'] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!topic.trim()) return
    if (status !== 'authenticated') {
      setError('Please sign in with Google first.')
      return
    }

    setLoading(true)
    setError(null)
    setBlogData(null)

    try {
      const tokenRes = await fetch('/api/auth/token')
      if (!tokenRes.ok) {
        throw new Error(tokenRes.status === 401 ? 'Session expired. Sign in again.' : 'Could not get auth token.')
      }
      const { token } = (await tokenRes.json()) as { token: string }

      const response = await fetch(`${apiBase}/create-blog`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ topic }),
      })

      if (response.status === 401) {
        throw new Error('Unauthorized — sign in again.')
      }
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data: BlogResponse = await response.json()
      setBlogData(data.response)
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const voices = ['Professional', 'Casual', 'Poetic', 'Academic', 'Journalistic']

  return (
    <div className="bg-[#f8f9fa] text-[#191c1d] min-h-screen font-body">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-stone-50/80 dark:bg-stone-900/80 backdrop-blur-xl border-b border-stone-200/20">
        <div className="flex justify-between items-center max-w-7xl mx-auto px-8 py-6">
          <div className="text-2xl font-serif italic text-emerald-900 dark:text-emerald-50">The Curator</div>
          <div className="hidden md:flex items-center space-x-12">
            <a className="text-stone-500 dark:text-stone-400 font-sans tracking-wide uppercase text-xs hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-300" href="#">Home</a>
            <a className="text-stone-500 dark:text-stone-400 font-sans tracking-wide uppercase text-xs hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-300" href="#">All Blogs</a>
            <a className="text-emerald-900 dark:text-emerald-50 border-b-2 border-emerald-900 dark:border-emerald-50 pb-1 font-sans tracking-wide uppercase text-xs" href="#">Create with AI</a>
          </div>
          <div className="flex items-center space-x-6">
            <Search className="w-5 h-5 text-emerald-900 cursor-pointer" />
            {status === 'loading' ? (
              <span className="font-label text-xs uppercase tracking-widest text-stone-400">…</span>
            ) : session ? (
              <div className="flex items-center gap-3">
                {session.user?.image ? (
                  <Image
                    src={session.user.image}
                    alt=""
                    width={36}
                    height={36}
                    className="h-9 w-9 rounded-full border border-stone-200 object-cover"
                  />
                ) : null}
                <span className="hidden max-w-[140px] truncate font-label text-xs text-stone-600 sm:inline">
                  {session.user?.name ?? session.user?.email}
                </span>
                <button
                  type="button"
                  onClick={() => signOut()}
                  className="rounded-md bg-stone-200 px-4 py-2 font-label text-sm tracking-wide text-stone-800 transition-transform active:scale-95 hover:bg-stone-300"
                >
                  Sign out
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => signIn('google')}
                className="rounded-md bg-[#012d1d] px-5 py-2 font-label text-sm tracking-wide text-white transition-transform active:scale-95 hover:opacity-90"
              >
                Sign in with Google
              </button>
            )}
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-20 px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">

          {/* Left Column: Input Panel */}
          <div className="lg:col-span-5 space-y-12">
            <header className="space-y-4">
              <h1 className="text-5xl font-serif leading-tight italic text-[#012d1d]">
                Draft your vision <br />with intelligence.
              </h1>
              <p className="text-[#4c616c] font-body leading-relaxed max-w-md">
                Our AI companion curates your thoughts into sophisticated, editorial-grade narratives. Begin your next masterpiece.
              </p>
            </header>

            <div className="space-y-8">
              {/* Prompt Area */}
              <div className="space-y-3">
                <label className="text-xs font-label uppercase tracking-widest text-[#4c616c] font-bold">The Creative Topic</label>
                <div className="relative group">
                  <textarea
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="w-full h-48 p-6 bg-stone-50 rounded-xl focus:ring-0 focus:outline-none border border-stone-200/50 resize-none font-body text-[#191c1d] text-lg leading-relaxed placeholder:text-stone-400 transition-colors focus:bg-white"
                    placeholder="Describe the essence of your story... e.g., 'The quiet morning rituals of a Kyoto tea master'"
                  />
                  <div className="absolute bottom-4 right-4 text-[10px] font-label text-stone-400 uppercase tracking-tighter">
                    {topic.length} / 2000 characters
                  </div>
                </div>
              </div>

              {/* Style Selection */}
              <div className="space-y-4">
                <label className="text-xs font-label uppercase tracking-widest text-[#4c616c] font-bold">Curatorial Voice</label>
                <div className="flex flex-wrap gap-3">
                  {voices.map((v) => (
                    <button
                      key={v}
                      onClick={() => setBlogKind(v)}
                      className={`px-5 py-2 rounded-full text-sm font-label transition-all ${blogKind === v
                          ? 'bg-[#012d1d] text-white'
                          : 'bg-[#cfe6f2] text-[#354a53] hover:bg-stone-200'
                        }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-4">
                <button
                  disabled={loading || !topic.trim() || status !== 'authenticated'}
                  onClick={handleGenerate}
                  className={`w-full py-5 bg-gradient-to-br from-[#012d1d] to-[#1b4332] text-white rounded-xl font-label text-lg tracking-widest uppercase flex items-center justify-center space-x-3 shadow-lg shadow-emerald-900/5 hover:opacity-90 transition-all active:scale-[0.98] ${(loading || !topic.trim() || status !== 'authenticated') ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Sparkles className="w-5 h-5" />
                  )}
                  <span>{loading ? 'Generating...' : 'Generate with AI'}</span>
                </button>
              </div>

              {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm font-label border border-red-100">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Preview Panel */}
          <div className="lg:col-span-7 flex flex-col">
            <div className={`bg-stone-50 rounded-2xl p-10 flex-grow relative min-h-[600px] border border-stone-200/50 ${loading ? 'opacity-60' : ''}`}>
              {!blogData && !loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-12 pointer-events-none">
                  <div className="w-24 h-24 mb-8 opacity-20">
                    <BookOpen className="w-24 h-24 text-[#012d1d]" />
                  </div>
                  <h3 className="font-serif text-3xl text-[#012d1d]/40 italic mb-4">Your manuscript will appear here</h3>
                  <p className="font-body text-[#4c616c]/50 max-w-xs text-sm leading-relaxed">
                    Once generated, you'll be able to edit, format, and curate your content using our editorial suite.
                  </p>
                </div>
              )}

              {loading && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-12 z-10">
                  <Loader2 className="w-12 h-12 text-[#012d1d] animate-spin mb-4" />
                  <p className="font-serif text-xl italic text-[#012d1d]">Curating your masterpiece...</p>
                  <p className="text-sm text-[#4c616c] mt-2">This may take up to a minute.</p>
                </div>
              )}

              {blogData && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000 ease-out">
                  <header className="mb-12 border-b border-stone-200/60 pb-12">
                    <div className="flex items-center space-x-3 mb-6">
                      <span className="px-3 py-1 bg-emerald-100 text-emerald-800 text-[10px] font-bold uppercase tracking-widest rounded-full">
                        {blogData.plan.blog_kind}
                      </span>
                      <span className="text-[10px] text-stone-400 font-bold uppercase tracking-widest leading-none">
                        • {blogData.plan.tone}
                      </span>
                    </div>
                    <h1 className="text-5xl font-serif italic text-[#012d1d] leading-tight mb-6">
                      {blogData.plan.blog_title}
                    </h1>
                    <div className="flex flex-wrap gap-2 mb-8">
                      {blogData.plan.tasks.flatMap(t => t.tags).filter((v, i, a) => a.indexOf(v) === i).map(tag => (
                        <span key={tag} className="text-[10px] font-label uppercase tracking-tighter text-stone-500 bg-stone-100 px-2 py-1 rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                    <p className="text-sm text-stone-500 font-body italic">
                      Curated for <span className="text-emerald-900 font-semibold">{blogData.plan.audience}</span> • {blogData.as_of}
                    </p>
                  </header>

                  <article className="prose prose-stone max-w-none space-y-12">
                    {blogData.sections.map(([id, content]) => (
                      <section key={id} className="relative group">
                        <ReactMarkdown
                          className="font-body text-lg leading-relaxed text-[#191c1d]"
                          components={{
                            h1: ({ node, ...props }) => <h1 className="text-4xl font-serif italic text-[#012d1d] mb-8" {...props} />,
                            h2: ({ node, ...props }) => <h2 className="text-2xl font-serif italic text-[#012d1d] mt-12 mb-6" {...props} />,
                            h3: ({ node, ...props }) => <h3 className="text-xl font-serif italic text-[#012d1d] mt-8 mb-4 border-l-2 border-emerald-900/20 pl-4" {...props} />,
                            p: ({ node, ...props }) => <p className="mb-6 opacity-90" {...props} />,
                            ul: ({ node, ...props }) => <ul className="list-disc pl-6 mb-6 space-y-3" {...props} />,
                            li: ({ node, ...props }) => <li className="text-base text-stone-700" {...props} />,
                            blockquote: ({ node, ...props }) => (
                              <blockquote className="border-l-4 border-emerald-900/30 pl-6 italic my-8 text-emerald-900/70" {...props} />
                            ),
                            code: ({ node, inline, className, children, ...props }: any) => {
                              const match = /language-(\w+)/.exec(className || '')
                              return !inline ? (
                                <div className="my-8 rounded-xl overflow-hidden border border-stone-200 shadow-sm">
                                  <div className="bg-stone-100 px-4 py-2 border-b border-stone-200 flex justify-between items-center">
                                    <span className="text-[10px] font-mono text-stone-400 uppercase">{match ? match[1] : 'code'}</span>
                                  </div>
                                  <pre className="p-6 bg-[#1e293b] text-blue-100 overflow-x-auto font-mono text-sm leading-relaxed">
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  </pre>
                                </div>
                              ) : (
                                <code className="bg-emerald-50 text-emerald-900 px-1.5 py-0.5 rounded font-mono text-sm" {...props}>
                                  {children}
                                </code>
                              )
                            }
                          }}
                        >
                          {content}
                        </ReactMarkdown>
                      </section>
                    ))}
                  </article>
                </div>
              )}

              {/* Editorial Metadata Floating Element */}
              <div className="absolute top-8 right-8">
                <div className="flex items-center space-x-3 bg-white px-4 py-2 rounded-full shadow-sm border border-stone-100">
                  <span className={`w-2 h-2 rounded-full ${loading ? 'bg-amber-400' : blogData ? 'bg-emerald-400' : 'bg-stone-300'}`}></span>
                  <span className="text-[10px] font-label uppercase tracking-widest text-stone-400">
                    {loading ? 'Generating' : blogData ? 'Ready' : 'Preview Mode'}
                  </span>
                </div>
              </div>
            </div>

            {/* Featured Image Hint */}
            <div className="mt-8 grid grid-cols-2 gap-8">
              <div className="bg-white rounded-xl p-6 flex items-center space-x-6 border border-stone-200/30">
                <div className="w-20 h-20 bg-[#c1ecd4] rounded-lg flex items-center justify-center">
                  <ImageIcon className="w-10 h-10 text-[#012d1d]" />
                </div>
                <div>
                  <p className="text-xs font-label uppercase tracking-widest text-stone-400 mb-1">AI Suggestion</p>
                  <h4 className="font-serif text-[#012d1d] italic">Matched Imagery</h4>
                </div>
              </div>
              <div className="bg-white rounded-xl p-6 flex items-center space-x-6 border border-stone-200/30">
                <div className="w-20 h-20 bg-[#cfe6f2] rounded-lg flex items-center justify-center">
                  <Tag className="w-10 h-10 text-[#4c616c]" />
                </div>
                <div>
                  <p className="text-xs font-label uppercase tracking-widest text-stone-400 mb-1">Taxonomy</p>
                  <h4 className="font-serif text-[#012d1d] italic">Auto-Tagging</h4>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-12 mt-20 bg-stone-100 dark:bg-stone-950 border-t border-stone-200/20">
        <div className="flex flex-col md:flex-row justify-between items-center px-8 max-w-7xl mx-auto">
          <div className="text-lg font-serif italic text-emerald-900 dark:text-emerald-50 mb-6 md:mb-0">The Curator</div>
          <div className="flex flex-col items-center md:items-end space-y-4">
            <div className="flex space-x-8">
              <a className="text-stone-400 font-sans text-xs tracking-widest uppercase hover:text-emerald-900 dark:hover:text-emerald-50 transition-opacity" href="#">Privacy</a>
              <a className="text-stone-400 font-sans text-xs tracking-widest uppercase hover:text-emerald-900 dark:hover:text-emerald-50 transition-opacity" href="#">Terms</a>
              <a className="text-stone-400 font-sans text-xs tracking-widest uppercase hover:text-emerald-900 dark:hover:text-emerald-50 transition-opacity" href="#">Contact</a>
            </div>
            <p className="text-stone-400 font-sans text-xs tracking-widest uppercase">© 2024 The Curator. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
