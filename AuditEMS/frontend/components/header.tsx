import { useSession, signOut } from "next-auth/react"

export default function Header() {
  const { data: session, status } = useSession()
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-background/80 backdrop-blur-md border-b border-border'
          : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 animate-fade-in-up">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <span className="font-bold text-xl text-foreground hidden sm:inline">
            AuditAI
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8">
          <Link
            href="#features"
            className="text-foreground/70 hover:text-foreground transition-colors"
          >
            Features
          </Link>
          <Link
            href="#upload"
            className="text-foreground/70 hover:text-foreground transition-colors"
          >
            Upload
          </Link>
          <Link
            href="#testimonials"
            className="text-foreground/70 hover:text-foreground transition-colors"
          >
            Testimonials
          </Link>
        </div>

        <div className="flex items-center gap-3">
          {status === "authenticated" ? (
            <>
              <span className="text-sm text-foreground/70 hidden sm:inline">
                Hi, {session.user?.name || session.user?.email}
              </span>
              <Button
                variant="outline"
                onClick={() => signOut()}
                className="border-border hover:bg-secondary bg-transparent"
              >
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Link href="/signin">
                <Button
                  variant="outline"
                  className="hidden sm:inline-flex border-border hover:bg-secondary bg-transparent"
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/signup">
                <Button className="bg-gradient-to-r from-primary to-accent hover:opacity-90 text-white">
                  Get Started
                </Button>
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
