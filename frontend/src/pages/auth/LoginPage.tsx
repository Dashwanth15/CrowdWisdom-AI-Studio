import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, Mail, User, ArrowRight, ShieldCheck } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { CrowdWisdomLogo } from '@/components/branding'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import toast from 'react-hot-toast'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login, register, isLoading } = useAuthStore()

  // Form states
  const [loginEmail, setLoginEmail] = useState('admin@crowdwisdom.ai')
  const [loginPassword, setLoginPassword] = useState('admin123')

  const [regEmail, setRegEmail] = useState('')
  const [regUsername, setRegUsername] = useState('')
  const [regFullName, setRegFullName] = useState('')
  const [regPassword, setRegPassword] = useState('')

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

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await register({
        email: regEmail,
        username: regUsername,
        full_name: regFullName,
        password: regPassword,
      })
      toast.success('Account created successfully!')
      navigate('/')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Registration failed. Try again.')
    }
  }

  return (
    <div className="min-h-screen w-screen flex flex-col items-center justify-center bg-[#080A0F] text-[#F2F3F5] p-4 relative overflow-hidden font-sans">
      {/* Subtle institutional ambient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-[#547DB8]/10 blur-[140px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md z-10 space-y-6">
        {/* Official Brand Header */}
        <CrowdWisdomLogo variant="auth" />

        {/* Auth Card */}
        <Card className="border-[#292E37] bg-[#15191F] shadow-2xl">
          <Tabs defaultValue="login" className="w-full">
            <CardHeader className="pb-3 border-b border-[#292E37]/60">
              <TabsList className="grid w-full grid-cols-2 bg-[#101216] border border-[#292E37]">
                <TabsTrigger value="login" className="data-[state=active]:bg-[#1B2028] data-[state=active]:text-[#F2F3F5]">Sign In</TabsTrigger>
                <TabsTrigger value="register" className="data-[state=active]:bg-[#1B2028] data-[state=active]:text-[#F2F3F5]">Register</TabsTrigger>
              </TabsList>
            </CardHeader>

            <CardContent className="pt-4">
              {/* Login Tab */}
              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="email" className="text-xs text-[#A0A7B2]">Email or Username</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-2.5 h-4 w-4 text-[#727B89]" />
                      <Input
                        id="email"
                        type="text"
                        placeholder="admin@crowdwisdom.ai"
                        className="pl-9 text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5] focus:border-[#547DB8]"
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="password" className="text-xs text-[#A0A7B2]">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-2.5 h-4 w-4 text-[#727B89]" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        className="pl-9 text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5] focus:border-[#547DB8]"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="pt-2">
                    <Button type="submit" variant="brand" className="w-full bg-[#547DB8] hover:bg-[#436494] text-white font-medium" disabled={isLoading}>
                      {isLoading ? 'Signing In...' : 'Access Command Center'}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>

                  <div className="rounded-lg bg-[#101216] border border-[#292E37] p-2.5 text-[11px] text-[#A0A7B2] flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="h-4 w-4 flex-shrink-0 text-[#36B58F]" />
                      <span>Demo credentials: <strong>admin@crowdwisdom.ai</strong> / <strong>admin123</strong></span>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setLoginEmail('admin@crowdwisdom.ai')
                        setLoginPassword('admin123')
                        toast.success('Credentials filled!')
                      }}
                      className="text-[10px] bg-[#C5A46D]/15 hover:bg-[#C5A46D]/30 text-[#C5A46D] px-2 py-0.5 rounded border border-[#C5A46D]/30 transition"
                    >
                      Fill
                    </button>
                  </div>
                </form>
              </TabsContent>

              {/* Register Tab */}
              <TabsContent value="register">
                <form onSubmit={handleRegister} className="space-y-3">
                  <div className="space-y-1">
                    <Label htmlFor="reg-name" className="text-xs text-[#A0A7B2]">Full Name</Label>
                    <Input
                      id="reg-name"
                      type="text"
                      placeholder="Institutional Strategist"
                      className="text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                      value={regFullName}
                      onChange={(e) => setRegFullName(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="reg-user" className="text-xs text-[#A0A7B2]">Username</Label>
                    <Input
                      id="reg-user"
                      type="text"
                      placeholder="strategist"
                      className="text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                      value={regUsername}
                      onChange={(e) => setRegUsername(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="reg-email" className="text-xs text-[#A0A7B2]">Email</Label>
                    <Input
                      id="reg-email"
                      type="email"
                      placeholder="trader@crowdwisdom.ai"
                      className="text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-1">
                    <Label htmlFor="reg-pass" className="text-xs text-[#A0A7B2]">Password</Label>
                    <Input
                      id="reg-pass"
                      type="password"
                      placeholder="••••••••"
                      className="text-xs bg-[#101216] border-[#292E37] text-[#F2F3F5]"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      required
                    />
                  </div>

                  <div className="pt-2">
                    <Button type="submit" variant="brand" className="w-full bg-[#547DB8] hover:bg-[#436494] text-white font-medium" disabled={isLoading}>
                      {isLoading ? 'Creating Account...' : 'Create Studio Account'}
                    </Button>
                  </div>
                </form>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>

        {/* Compliance Footer */}
        <p className="text-center text-[11px] text-[#727B89] font-mono">
          CrowdWisdomTrading.com • Collective Market Sentiment & Financial Intelligence
        </p>
      </div>
    </div>
  )
}
