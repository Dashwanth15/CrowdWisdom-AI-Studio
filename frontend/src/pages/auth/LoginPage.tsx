import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Lock,
  Mail,
  User,
  UserCheck,
  ArrowRight,
  ShieldCheck,
  Eye,
  EyeOff,
  Sparkles,
  Play,
  Film,
  TrendingUp,
  Sliders,
  CheckCircle2,
  Volume2,
  Loader2,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import toast from 'react-hot-toast'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, register, isLoading } = useAuthStore()

  // Tab State: 'login' | 'register'
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login')

  // Password Visibility Toggles
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [showRegPassword, setShowRegPassword] = useState(false)

  // Login Form States (pre-filled with canonical demo credentials)
  const [loginEmail, setLoginEmail] = useState('admin@crowdwisdom.ai')
  const [loginPassword, setLoginPassword] = useState('admin123')

  // Register Form States
  const [regFullName, setRegFullName] = useState('')
  const [regUsername, setRegUsername] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')

  // Handle Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await login(loginEmail, loginPassword)
      toast.success('Welcome back to CrowdWisdom AI Studio!')
      navigate('/')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid email or password.')
    }
  }

  // Handle Register
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await register({
        email: regEmail,
        username: regUsername,
        full_name: regFullName,
        password: regPassword,
      })
      toast.success('Account created successfully! Welcome to the Studio.')
      navigate('/')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed. Try again.')
    }
  }

  // Handle Demo Fill
  const handleFillDemo = () => {
    setLoginEmail('admin@crowdwisdom.ai')
    setLoginPassword('admin123')
    toast.success('Demo credentials loaded (admin@crowdwisdom.ai)')
  }

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#080B12] text-[#F2F3F5] relative overflow-hidden font-sans selection:bg-[#38BDF8]/20 selection:text-[#F8FAFC]">
      {/* ========================================================================= */}
      {/* LEFT SECTION — Premium Editorial Product Experience                       */}
      {/* ========================================================================= */}
      <div className="w-full lg:w-[58%] xl:w-[60%] flex flex-col justify-between p-6 sm:p-10 lg:p-12 xl:p-16 relative overflow-hidden bg-[#080B12] border-b lg:border-b-0 lg:border-r border-[#1B2230]">
        {/* Subtle, Restrained Atmospheric Lighting (Linear/Apple Style) */}
        <div className="absolute -top-40 -left-40 w-[550px] h-[550px] bg-gradient-to-br from-[#1E293B]/20 via-[#0EA5E9]/5 to-transparent blur-[140px] pointer-events-none" />
        <div className="absolute -bottom-40 right-10 w-[500px] h-[500px] bg-gradient-to-tl from-[#1E293B]/25 via-[#C5A46D]/5 to-transparent blur-[150px] pointer-events-none" />

        {/* ----------------------------------------------------------------------- */}
        {/* TOP BRAND HEADER                                                        */}
        {/* ----------------------------------------------------------------------- */}
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            {/* Official Bears & Bulls Logo Badge Container */}
            <div className="relative h-10 w-16 sm:h-11 sm:w-18 rounded-lg bg-white p-1 border border-[#38BDF8]/30 shadow-md flex items-center justify-center overflow-hidden flex-shrink-0">
              <img
                src="/crowdwisdom_logo_badge.png"
                alt="CrowdWisdom Official Brand Symbol"
                className="h-full w-full object-contain select-none"
                loading="eager"
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-[#F8FAFC] uppercase">
                  CrowdWisdom
                </span>
                <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-[#C5A46D]/15 text-[#C5A46D] border border-[#C5A46D]/30 tracking-wider">
                  PRO STUDIO
                </span>
              </div>
              <p className="text-[11px] font-mono text-[#788599] tracking-wide">
                AI MARKETING INTELLIGENCE PLATFORM
              </p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-[#6E7D93]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#34D399]" />
            <span>Autonomous Pipeline Active</span>
          </div>
        </div>

        {/* ----------------------------------------------------------------------- */}
        {/* HERO STORYTELLING & EDITORIAL HEADLINE                                  */}
        {/* ----------------------------------------------------------------------- */}
        <div className="relative z-10 my-8 sm:my-10 space-y-6 max-w-2xl">
          <div className="space-y-3">
            <h1 className="text-3xl sm:text-4xl lg:text-[44px] xl:text-[48px] font-extrabold tracking-[-0.03em] text-[#F8FAFC] leading-[1.12]">
              From Marketing Intelligence <br className="hidden sm:inline" />
              <span className="text-[#94A3B8] font-normal">to </span>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#F8FAFC] via-[#CBD5E1] to-[#38BDF8]">
                Cinematic Impact.
              </span>
            </h1>
            <p className="text-sm sm:text-[15px] text-[#8E9BAE] leading-relaxed max-w-xl font-normal">
              Research markets. Discover opportunities. Create compelling campaigns. Produce
              cinematic advertisements — all through one intelligent AI-powered platform.
            </p>
          </div>

          {/* --------------------------------------------------------------------- */}
          {/* THE CENTERPIECE: Editorial Campaign & Cinematic Production Canvas     */}
          {/* --------------------------------------------------------------------- */}
          <div className="relative rounded-2xl bg-[#0D121B] border border-[#1E2636] shadow-[0_20px_50px_rgba(0,0,0,0.6)] overflow-hidden">
            {/* Top Stage Progression Ribbon */}
            <div className="px-4 py-2.5 bg-[#0A0E15] border-b border-[#1A2230] flex items-center justify-between text-[11px] font-mono text-[#717E91]">
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-2 h-2 rounded-full bg-[#34D399]" />
                <span className="text-[#CBD5E1] font-semibold">STAGE 03</span>
                <span className="text-[#475569]">/</span>
                <span className="text-[#94A3B8]">AI CINEMATIC PRODUCTION</span>
              </div>
              <div className="flex items-center gap-3 text-[10px]">
                <span className="text-[#64748B]">Resolution: <strong className="text-[#E2E8F0] font-mono">4K UHD</strong></span>
                <span className="text-[#475569]">•</span>
                <span className="text-[#64748B]">Framerate: <strong className="text-[#E2E8F0] font-mono">60 FPS</strong></span>
              </div>
            </div>

            {/* Video Viewport Showcase Frame */}
            <div className="relative aspect-[16/9] w-full overflow-hidden bg-black group">
              {/* Primary Cinematic Creative Preview Image */}
              <img
                src="/showcase/cinematic_ad_preview.jpg"
                alt="CrowdWisdom Cinematic Advertisement Master"
                className="w-full h-full object-cover object-center select-none transition-transform duration-700 group-hover:scale-[1.02]"
                loading="eager"
                onError={(e) => {
                  // Fallback to platform preview if thumb is unavailable
                  ;(e.target as HTMLImageElement).src = '/showcase/platform_preview.jpg'
                }}
              />

              {/* Cinematic Vignette Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-[#0A0D14] via-transparent to-black/40 pointer-events-none" />

              {/* Floating Top In-Video Telemetry Overlay */}
              <div className="absolute top-3 left-3 right-3 flex items-center justify-between text-xs pointer-events-none">
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-black/70 backdrop-blur-md border border-white/10 text-[10px] font-mono text-white/90 shadow-sm">
                  <Film className="h-3 w-3 text-[#38BDF8]" />
                  <span>Scene 02: "The Sentiment Divergence"</span>
                </div>
                <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#C5A46D]/20 backdrop-blur-md border border-[#C5A46D]/40 text-[9px] font-mono text-[#C5A46D] font-semibold uppercase">
                  Broadcast Mastered
                </div>
              </div>

              {/* Center Play Indicator */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="h-12 w-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center shadow-lg transition-transform duration-300 group-hover:scale-110">
                  <Play className="h-5 w-5 text-white fill-white ml-0.5" />
                </div>
              </div>

              {/* Bottom Scrubber Timeline Strip Overlay */}
              <div className="absolute bottom-0 inset-x-0 p-3 pt-6 bg-gradient-to-t from-[#0A0E17] via-[#0A0E17]/90 to-transparent space-y-2">
                {/* Scene Timeline Blocks */}
                <div className="grid grid-cols-4 gap-1 text-[9px] font-mono">
                  <div className="py-1 px-1.5 rounded bg-white/10 border border-white/10 text-[#94A3B8] truncate">
                    01 Hook (0-5s)
                  </div>
                  <div className="py-1 px-1.5 rounded bg-[#38BDF8]/20 border border-[#38BDF8]/40 text-[#38BDF8] font-semibold truncate">
                    02 Sentiment (5-14s)
                  </div>
                  <div className="py-1 px-1.5 rounded bg-white/5 border border-white/5 text-[#64748B] truncate">
                    03 Edge (14-23s)
                  </div>
                  <div className="py-1 px-1.5 rounded bg-white/5 border border-white/5 text-[#64748B] truncate">
                    04 CTA (23-30s)
                  </div>
                </div>

                {/* Scrubber Progress Bar */}
                <div className="space-y-1">
                  <div className="relative h-1 w-full rounded-full bg-white/10 overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-[#38BDF8] to-[#60A5FA] w-[46%]" />
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-[#717E91]">
                    <span className="text-[#CBD5E1]">00:14.28 / 00:30.00</span>
                    <span className="flex items-center gap-1 text-[#94A3B8]">
                      <Volume2 className="h-3 w-3 text-[#38BDF8]" />
                      <span>Neural Voice & Score Synthesized</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Artifact Metadata Bar */}
            <div className="p-3.5 bg-[#0C1017] border-t border-[#1A2230] grid grid-cols-3 gap-3 text-xs">
              <div className="space-y-0.5">
                <span className="text-[10px] font-mono text-[#64748B] uppercase">Market Source</span>
                <p className="text-[11px] font-semibold text-[#E2E8F0] truncate">Meta & Google Ad Intel</p>
              </div>
              <div className="space-y-0.5">
                <span className="text-[10px] font-mono text-[#64748B] uppercase">Creative Engine</span>
                <p className="text-[11px] font-semibold text-[#38BDF8] truncate">Hermes Multi-Agent</p>
              </div>
              <div className="space-y-0.5 text-right">
                <span className="text-[10px] font-mono text-[#64748B] uppercase">Render Pipeline</span>
                <p className="text-[11px] font-semibold text-[#C5A46D] truncate">OpenMontage v2</p>
              </div>
            </div>
          </div>
        </div>

        {/* ----------------------------------------------------------------------- */}
        {/* REFINED EDITORIAL TRUST STRIP                                           */}
        {/* ----------------------------------------------------------------------- */}
        <div className="relative z-10 pt-4 border-t border-[#1A2230] flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-[#64748B]">
          <div className="flex flex-wrap items-center gap-4 sm:gap-6">
            <span className="text-[#8E9BAE]">Enterprise Multi-Agent Architecture</span>
            <span className="text-[#334155]">•</span>
            <span className="text-[#8E9BAE]">Broadcast-Grade 4K Neural Video</span>
            <span className="text-[#334155]">•</span>
            <span className="text-[#8E9BAE]">Real-Time Market Sentiment</span>
          </div>

          <span className="text-[11px] text-[#475569]">
            CrowdWisdomTrading.com
          </span>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* RIGHT SECTION — Authentication Command Panel (Sign In & Register)         */}
      {/* ========================================================================= */}
      <div className="w-full lg:w-[42%] xl:w-[40%] flex items-center justify-center p-6 sm:p-10 lg:p-12 relative bg-[#090C13] border-t lg:border-t-0 lg:border-l border-[#1B2230]">
        {/* Subtle Ambient Glow */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-[#2563EB]/8 blur-[120px] rounded-full pointer-events-none" />

        <div className="w-full max-w-[420px] z-10 space-y-6">
          {/* Mobile Header (visible only on small screens) */}
          <div className="lg:hidden text-center space-y-2 pb-2">
            <div className="inline-block relative">
              <div className="relative h-12 w-24 rounded-lg bg-white p-1 border border-[#38BDF8]/40 shadow-md flex items-center justify-center mx-auto overflow-hidden">
                <img
                  src="/crowdwisdom_logo_badge.png"
                  alt="CrowdWisdom Logo"
                  className="h-full w-full object-contain"
                />
              </div>
            </div>
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg font-bold tracking-tight text-[#F2F3F5] uppercase">
                CrowdWisdom
              </span>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#C5A46D]/15 text-[#C5A46D] border border-[#C5A46D]/30">
                PRO STUDIO
              </span>
            </div>
          </div>

          {/* Primary Form Card */}
          <div className="relative rounded-2xl bg-[#111622]/90 border border-[#222B38] p-6 sm:p-8 backdrop-blur-xl shadow-2xl space-y-6">
            {/* Header / Intro */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#38BDF8] px-2 py-0.5 rounded bg-[#38BDF8]/10 border border-[#38BDF8]/25 font-semibold">
                  Institutional Access
                </span>
                <span className="text-[11px] font-mono text-[#6A7688]">
                  {activeTab === 'login' ? 'Authentication' : 'Registration'}
                </span>
              </div>

              <h2 className="text-2xl font-bold tracking-tight text-[#F2F3F5] pt-1">
                {activeTab === 'login' ? 'Welcome Back.' : 'Create Studio Account.'}
              </h2>
              <p className="text-xs text-[#94A3B8]">
                {activeTab === 'login'
                  ? 'Sign in to continue to your creative command center.'
                  : 'Deploy autonomous AI marketing agents for your operations.'}
              </p>
            </div>

            {/* Tab Switcher */}
            <div className="grid grid-cols-2 p-1 rounded-xl bg-[#0B0E15] border border-[#1F2937]">
              <button
                type="button"
                onClick={() => setActiveTab('login')}
                className={`py-2 text-xs font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
                  activeTab === 'login'
                    ? 'bg-[#1C2433] text-[#F2F3F5] border border-[#2D3A4F] shadow-sm'
                    : 'text-[#788292] hover:text-[#D1D5DB]'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('register')}
                className={`py-2 text-xs font-semibold rounded-lg transition-all duration-200 cursor-pointer ${
                  activeTab === 'register'
                    ? 'bg-[#1C2433] text-[#F2F3F5] border border-[#2D3A4F] shadow-sm'
                    : 'text-[#788292] hover:text-[#D1D5DB]'
                }`}
              >
                Register
              </button>
            </div>

            {/* =================================================================== */}
            {/* SIGN IN FORM                                                        */}
            {/* =================================================================== */}
            {activeTab === 'login' ? (
              <form onSubmit={handleLogin} className="space-y-4">
                {/* Email or Username */}
                <div className="space-y-1.5">
                  <Label htmlFor="login-email" className="text-xs font-medium text-[#C8D1DC]">
                    Email or Username
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="login-email"
                      type="text"
                      placeholder="admin@crowdwisdom.ai"
                      className="pl-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      required
                      autoComplete="username"
                    />
                  </div>
                </div>

                {/* Password Field with Visibility Toggle */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="login-password" className="text-xs font-medium text-[#C8D1DC]">
                      Password
                    </Label>
                    <span className="text-[10px] font-mono text-[#6A7688]">
                      Default: admin123
                    </span>
                  </div>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="login-password"
                      type={showLoginPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="pl-10 pr-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      required
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowLoginPassword(!showLoginPassword)}
                      className="absolute right-3 top-3 text-[#606E82] hover:text-[#F2F3F5] transition-colors cursor-pointer"
                      title={showLoginPassword ? 'Hide password' : 'Show password'}
                    >
                      {showLoginPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit CTA Button */}
                <div className="pt-2">
                  <Button
                    type="submit"
                    className="w-full h-10 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] hover:from-[#3B82F6] hover:to-[#2563EB] text-white font-medium shadow-[0_0_20px_rgba(37,99,235,0.35)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)] transition-all duration-200 cursor-pointer flex items-center justify-center gap-2"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Authenticating...</span>
                      </>
                    ) : (
                      <>
                        <span>Access Command Center</span>
                        <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>

                {/* Demo Credentials Helper Box (Exact Preservation of Demo Architecture) */}
                <div className="rounded-xl bg-[#0D121B] border border-[#222D3E] p-3 text-xs text-[#94A3B8] flex items-center justify-between gap-2 shadow-inner">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="p-1 rounded bg-[#34D399]/10 border border-[#34D399]/20 flex-shrink-0">
                      <ShieldCheck className="h-3.5 w-3.5 text-[#34D399]" />
                    </div>
                    <div className="min-w-0 truncate text-[11px]">
                      <span className="text-[#64748B]">Demo: </span>
                      <strong className="text-[#E2E8F0] font-mono">admin@crowdwisdom.ai</strong>
                      <span className="text-[#64748B]"> / </span>
                      <strong className="text-[#E2E8F0] font-mono">admin123</strong>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleFillDemo}
                    className="flex-shrink-0 text-[10px] font-mono font-semibold bg-[#C5A46D]/15 hover:bg-[#C5A46D]/30 text-[#C5A46D] px-2.5 py-1 rounded-md border border-[#C5A46D]/35 transition-all duration-150 cursor-pointer active:scale-95"
                    title="Populate administrative demo credentials"
                  >
                    Fill
                  </button>
                </div>
              </form>
            ) : (
              /* =================================================================== */
              /* REGISTER FORM                                                       */
              /* =================================================================== */
              <form onSubmit={handleRegister} className="space-y-3.5">
                {/* Full Name */}
                <div className="space-y-1">
                  <Label htmlFor="reg-fullname" className="text-xs font-medium text-[#C8D1DC]">
                    Full Name
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="reg-fullname"
                      type="text"
                      placeholder="Institutional Strategist"
                      className="pl-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={regFullName}
                      onChange={(e) => setRegFullName(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Username */}
                <div className="space-y-1">
                  <Label htmlFor="reg-username" className="text-xs font-medium text-[#C8D1DC]">
                    Username
                  </Label>
                  <div className="relative">
                    <UserCheck className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="reg-username"
                      type="text"
                      placeholder="strategist"
                      className="pl-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={regUsername}
                      onChange={(e) => setRegUsername(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="space-y-1">
                  <Label htmlFor="reg-email" className="text-xs font-medium text-[#C8D1DC]">
                    Email Address
                  </Label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="reg-email"
                      type="email"
                      placeholder="trader@crowdwisdom.ai"
                      className="pl-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Password with Visibility Toggle */}
                <div className="space-y-1">
                  <Label htmlFor="reg-password" className="text-xs font-medium text-[#C8D1DC]">
                    Password
                  </Label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-3 h-4 w-4 text-[#606E82]" />
                    <Input
                      id="reg-password"
                      type={showRegPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      className="pl-10 pr-10 h-10 text-xs bg-[#0C1017] border-[#222C3B] text-[#F2F3F5] placeholder:text-[#525E70] focus-visible:border-[#38BDF8] focus-visible:ring-1 focus-visible:ring-[#38BDF8]/40 rounded-lg transition-colors"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowRegPassword(!showRegPassword)}
                      className="absolute right-3 top-3 text-[#606E82] hover:text-[#F2F3F5] transition-colors cursor-pointer"
                      title={showRegPassword ? 'Hide password' : 'Show password'}
                    >
                      {showRegPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Register Submit Button */}
                <div className="pt-2">
                  <Button
                    type="submit"
                    className="w-full h-10 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] hover:from-[#3B82F6] hover:to-[#2563EB] text-white font-medium shadow-[0_0_20px_rgba(37,99,235,0.35)] hover:shadow-[0_0_25px_rgba(37,99,235,0.5)] transition-all duration-200 cursor-pointer flex items-center justify-center gap-2"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Creating Account...</span>
                      </>
                    ) : (
                      <>
                        <span>Create Studio Account</span>
                        <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>

                <p className="text-[10px] text-[#64748B] text-center leading-normal pt-1">
                  By registering, you agree to CrowdWisdom's Enterprise Master Services Agreement and Privacy Standards.
                </p>
              </form>
            )}
          </div>

          {/* Compliance & Attributions Footer */}
          <div className="text-center space-y-1">
            <p className="text-[11px] text-[#717E91] font-mono">
              CrowdWisdomTrading.com • Collective Market Sentiment & Financial Intelligence
            </p>
            <p className="text-[10px] text-[#4A5568] font-mono">
              Protected by Enterprise Multi-Agent Token Encryption & Session Guards
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
