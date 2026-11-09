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
  Cpu,
  Clapperboard,
  TrendingUp,
  Activity,
  Globe,
  Loader2,
  CheckCircle2,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '@/stores/authStore'
import { CrowdWisdomLogo } from '@/components/branding'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import toast from 'react-hot-toast'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, register, isLoading } = useAuthStore()

  // Tab State
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login')

  // Password Visibility Toggles
  const [showLoginPassword, setShowLoginPassword] = useState(false)
  const [showRegPassword, setShowRegPassword] = useState(false)

  // Login Form States (pre-filled with demo credentials as per project architecture)
  const [loginEmail, setLoginEmail] = useState('admin@crowdwisdom.ai')
  const [loginPassword, setLoginPassword] = useState('admin123')

  // Register Form States
  const [regFullName, setRegFullName] = useState('')
  const [regUsername, setRegUsername] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')

  // Handle Login Submission
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

  // Handle Registration Submission
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

  // Handle Demo Fill Action
  const handleFillDemo = () => {
    setLoginEmail('admin@crowdwisdom.ai')
    setLoginPassword('admin123')
    toast.success('Demo credentials loaded (admin@crowdwisdom.ai)')
  }

  // Capability Highlights
  const capabilities = [
    {
      icon: Cpu,
      title: 'Autonomous AI Agents',
      description: 'Hermes multi-agent swarm orchestrating ad research, hook synthesis, and pipeline automation.',
      badge: 'Hermes Swarm',
      badgeColor: 'text-[#38BDF8] border-[#38BDF8]/30 bg-[#38BDF8]/10',
      iconColor: 'text-[#38BDF8]',
      iconBg: 'bg-[#38BDF8]/10 border-[#38BDF8]/20',
    },
    {
      icon: Sparkles,
      title: 'Creative Intelligence',
      description: 'Dynamic consumer sentiment analysis across Meta, TikTok, and Google to generate winning hooks.',
      badge: 'Real-Time Insights',
      badgeColor: 'text-[#C5A46D] border-[#C5A46D]/30 bg-[#C5A46D]/10',
      iconColor: 'text-[#C5A46D]',
      iconBg: 'bg-[#C5A46D]/10 border-[#C5A46D]/20',
    },
    {
      icon: Clapperboard,
      title: 'Cinematic Video Production',
      description: 'OpenMontage neural engine generating broadcast-grade 4K 60fps video with AI voice synthesis.',
      badge: '4K HDR Engine',
      badgeColor: 'text-[#818CF8] border-[#818CF8]/30 bg-[#818CF8]/10',
      iconColor: 'text-[#818CF8]',
      iconBg: 'bg-[#818CF8]/10 border-[#818CF8]/20',
    },
    {
      icon: TrendingUp,
      title: 'Campaign Analytics',
      description: 'Unified cross-channel performance telemetry, conversion prediction, and automated iterations.',
      badge: 'Market Telemetry',
      badgeColor: 'text-[#34D399] border-[#34D399]/30 bg-[#34D399]/10',
      iconColor: 'text-[#34D399]',
      iconBg: 'bg-[#34D399]/10 border-[#34D399]/20',
    },
  ]

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#080B12] text-[#F2F3F5] relative overflow-hidden font-sans selection:bg-[#38BDF8]/30 selection:text-[#F2F3F5]">
      {/* ========================================================================= */}
      {/* LEFT SECTION — Brand Experience, Intelligence Network & Capabilities      */}
      {/* ========================================================================= */}
      <div className="w-full lg:w-[58%] xl:w-[60%] flex flex-col justify-between p-6 sm:p-10 lg:p-14 xl:p-16 relative overflow-hidden bg-gradient-to-br from-[#06080D] via-[#090D15] to-[#0E1522] border-b lg:border-b-0 lg:border-r border-[#1F2937]/60">
        {/* Subtle Ambient Radial Lighting */}
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-[#38BDF8]/10 blur-[130px] rounded-full pointer-events-none" />
        <div className="absolute top-1/2 -right-20 w-80 h-80 bg-[#6366F1]/10 blur-[140px] rounded-full pointer-events-none" />
        <div className="absolute -bottom-24 left-1/3 w-96 h-96 bg-[#C5A46D]/10 blur-[150px] rounded-full pointer-events-none" />

        {/* Subtle Engineering Dot Grid Overlay */}
        <div className="absolute inset-0 bg-dot-grid opacity-35 pointer-events-none mask-radial-faded" />

        {/* Top Brand Bar */}
        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {/* Official Bears & Bulls Logo Badge Container */}
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-[#38BDF8]/40 via-[#547DB8]/30 to-[#C5A46D]/40 rounded-xl blur-md opacity-60 group-hover:opacity-100 transition duration-300" />
              <div className="relative h-11 w-20 rounded-lg bg-white p-1 border border-[#38BDF8]/50 shadow-lg flex items-center justify-center overflow-hidden">
                <img
                  src="/crowdwisdom_logo_badge.png"
                  alt="CrowdWisdom Official Brand Symbol"
                  className="h-full w-full object-contain select-none"
                  loading="eager"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-base sm:text-lg font-bold tracking-tight text-[#F2F3F5] uppercase">
                  CrowdWisdom
                </span>
                <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-[#C5A46D]/15 text-[#C5A46D] border border-[#C5A46D]/35 tracking-wider">
                  PRO STUDIO
                </span>
              </div>
              <p className="text-[11px] font-mono text-[#8E9EB5] tracking-wide">
                AI MARKETING INTELLIGENCE PLATFORM
              </p>
            </div>
          </div>

          {/* Real-time System Operational Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#10141C]/80 border border-[#232B38] text-[11px] font-mono text-[#A0A7B2] backdrop-blur-sm shadow-sm w-fit">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#34D399] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#34D399]" />
            </span>
            <span className="text-[#34D399] font-medium">SYSTEM OPERATIONAL</span>
            <span className="text-[#3A4556]">•</span>
            <span>v2.5 PRO</span>
          </div>
        </div>

        {/* Middle Hero Presentation */}
        <div className="relative z-10 my-10 sm:my-12 lg:my-14 space-y-8 max-w-2xl">
          {/* Eyebrow Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-[#161D29]/80 border border-[#283548] text-xs font-mono text-[#38BDF8] shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-[#38BDF8]" />
            <span>Autonomous Cinematic Marketing Architecture</span>
          </div>

          {/* Primary Headline */}
          <div className="space-y-3">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-[#F2F3F5] leading-[1.12]">
              Intelligence That Turns{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#60A5FA] via-[#38BDF8] to-[#C5A46D]">
                Creativity Into Impact.
              </span>
            </h1>
            <p className="text-sm sm:text-base text-[#94A3B8] leading-relaxed max-w-xl">
              An autonomous AI marketing intelligence platform engineered to research, strategize,
              create and produce cinematic advertising experiences at scale.
            </p>
          </div>

          {/* Capability Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            {capabilities.map((cap) => {
              const Icon = cap.icon
              return (
                <div
                  key={cap.title}
                  className="group relative p-4 rounded-xl bg-[#10141C]/80 border border-[#1F2937]/80 hover:border-[#38BDF8]/40 transition-all duration-300 backdrop-blur-md shadow-sm hover:shadow-[0_4px_20px_-4px_rgba(56,189,248,0.15)] hover:-translate-y-0.5"
                >
                  <div className="flex items-start justify-between gap-2 mb-2.5">
                    <div className={`p-2 rounded-lg border ${cap.iconBg}`}>
                      <Icon className={`h-4 w-4 ${cap.iconColor}`} />
                    </div>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${cap.badgeColor}`}>
                      {cap.badge}
                    </span>
                  </div>
                  <h3 className="text-xs font-semibold text-[#F2F3F5] mb-1 group-hover:text-[#38BDF8] transition-colors">
                    {cap.title}
                  </h3>
                  <p className="text-[11px] text-[#788292] leading-relaxed">
                    {cap.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Bottom Trust & Compliance Strip */}
        <div className="relative z-10 pt-6 border-t border-[#1F2937]/60 flex flex-wrap items-center justify-between gap-4 text-xs font-mono text-[#788292]">
          <div className="flex flex-wrap items-center gap-4 sm:gap-6">
            <span className="flex items-center gap-1.5 text-[#A0A7B2]">
              <ShieldCheck className="h-4 w-4 text-[#34D399]" />
              <span>SOC2 Type II Ready</span>
            </span>
            <span className="flex items-center gap-1.5 text-[#A0A7B2]">
              <Lock className="h-4 w-4 text-[#38BDF8]" />
              <span>End-to-End Cryptographic Secret Vault</span>
            </span>
            <span className="flex items-center gap-1.5 text-[#A0A7B2]">
              <Globe className="h-4 w-4 text-[#C5A46D]" />
              <span>Global CDN Edge Acceleration</span>
            </span>
          </div>

          <span className="text-[11px] text-[#556070]">
            CrowdWisdomTrading.com
          </span>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* RIGHT SECTION — Authentication Command Panel (Sign In & Register)         */}
      {/* ========================================================================= */}
      <div className="w-full lg:w-[42%] xl:w-[40%] flex items-center justify-center p-6 sm:p-10 lg:p-12 relative bg-[#090C13] border-t lg:border-t-0 lg:border-l border-[#1F2937]/70">
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
