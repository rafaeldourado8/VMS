import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  Video, 
  ShieldCheck, 
  Cpu, 
  ScanFace, 
  Zap, 
  Globe, 
  ArrowRight, 
  PlayCircle,
  CheckCircle2
} from 'lucide-react';

// --- Componentes de Animação Reutilizáveis ---

const FadeInUp = ({ children, delay = 0, className = "" }: { children: React.ReactNode, delay?: number, className?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.8, delay, type: "spring", bounce: 0.4 }}
    className={className}
  >
    {children}
  </motion.div>
);

const FeatureCard = ({ icon: Icon, title, desc, index }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.5, delay: index * 0.1 }}
    whileHover={{ scale: 1.02, translateY: -5 }}
    className="group relative p-8 rounded-3xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent backdrop-blur-md overflow-hidden hover:border-primary/30 transition-colors"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    
    <div className="relative z-10">
      <div className="h-14 w-14 rounded-2xl bg-primary/20 flex items-center justify-center mb-6 text-primary group-hover:scale-110 transition-transform duration-300">
        <Icon size={28} />
      </div>
      <h3 className="text-2xl font-bold mb-3 text-foreground group-hover:text-primary transition-colors">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  </motion.div>
);

const Landing = () => {
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll();
  
  // Efeitos Parallax
  const yBg = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacityHero = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary selection:text-white">
      
      {/* --- Navbar --- */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100, damping: 20 }}
        className="fixed top-0 left-0 right-0 z-50 px-6 py-4 flex justify-between items-center backdrop-blur-lg border-b border-white/5 bg-background/70"
      >
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <div className="p-2 bg-gradient-to-tr from-primary to-purple-600 rounded-xl shadow-lg shadow-primary/20">
            <Video className="text-white h-6 w-6" />
          </div>
          <span className="text-xl font-bold tracking-tight">GT-Vision</span>
        </div>
        <div className="flex gap-4">
          <Button variant="ghost" className="hidden sm:flex hover:bg-white/5" onClick={() => navigate('/login')}>Login</Button>
          <Button onClick={() => navigate('/login')} className="rounded-full px-6 shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all">
            Acessar Sistema
          </Button>
        </div>
      </motion.header>

      {/* --- Hero Section --- */}
      <section className="relative min-h-screen flex items-center justify-center pt-20 px-6">
        {/* Background Dinâmico */}
        <div className="absolute inset-0 overflow-hidden -z-10">
          <motion.div style={{ y: yBg }} className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-primary/15 rounded-full blur-[150px]" />
          <motion.div style={{ y: yBg }} className="absolute bottom-[-10%] right-[-20%] w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[150px]" />
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>
        </div>

        <div className="container max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <motion.div style={{ opacity: opacityHero }} className="space-y-8 text-center lg:text-left z-10">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm font-medium backdrop-blur-md"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="bg-gradient-to-r from-primary to-purple-400 bg-clip-text text-transparent font-bold">Novo:</span> Módulo de IA Ativado
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1]">
              Segurança Inteligente <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-purple-500 to-pink-500">
                em Tempo Real
              </span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Plataforma VMS de última geração com detecção LPR integrada, processamento distribuído e interface ultra-responsiva.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-4">
              <Button size="lg" className="h-14 px-8 text-lg rounded-full gap-2 shadow-xl shadow-primary/20 hover:scale-105 transition-transform" onClick={() => navigate('/login')}>
                Começar Agora <ArrowRight className="h-5 w-5" />
              </Button>
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full gap-2 border-white/10 hover:bg-white/5 hover:text-primary" onClick={() => navigate('/login')}>
                Ver Demonstração <PlayCircle className="h-5 w-5" />
              </Button>
            </div>

            <div className="pt-8 flex items-center justify-center lg:justify-start gap-8 text-muted-foreground/60">
              <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-primary" /> Setup Instantâneo</div>
              <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-primary" /> 99.9% Uptime</div>
            </div>
          </motion.div>

          {/* Hero Visual Mockup */}
          <motion.div
            initial={{ opacity: 0, x: 100, rotateY: -20 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            transition={{ duration: 1, type: "spring", bounce: 0.2 }}
            className="relative hidden lg:block perspective-1000"
          >
            <div className="relative z-10 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden transform hover:rotate-y-6 hover:rotate-x-6 transition-transform duration-700 ease-out">
              {/* Mockup Header */}
              <div className="h-10 border-b border-white/10 bg-white/5 flex items-center px-4 gap-2">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-500/80"/>
                  <div className="h-3 w-3 rounded-full bg-yellow-500/80"/>
                  <div className="h-3 w-3 rounded-full bg-green-500/80"/>
                </div>
                <div className="ml-4 h-1.5 w-32 rounded-full bg-white/10"/>
              </div>
              
              {/* Mockup Body */}
              <div className="p-6 grid grid-cols-3 gap-4">
                <div className="col-span-2 row-span-2 aspect-video rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 relative overflow-hidden border border-white/10 group">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Video className="text-white/10 h-20 w-20 group-hover:text-primary/50 group-hover:scale-110 transition-all duration-500" />
                  </div>
                  <div className="absolute top-3 right-3 flex gap-2">
                    <div className="bg-red-500/20 border border-red-500/30 text-red-500 text-[10px] font-bold px-2 py-1 rounded backdrop-blur-md flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse"/> LIVE
                    </div>
                  </div>
                  {/* Scan Line Animation */}
                  <div className="absolute top-0 left-0 right-0 h-1 bg-primary/50 shadow-[0_0_20px_rgba(124,58,237,0.5)] animate-[scan_3s_ease-in-out_infinite]"/>
                </div>

                <div className="rounded-xl bg-white/5 border border-white/10 p-4 flex flex-col justify-between">
                  <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary mb-2"><ScanFace size={18}/></div>
                  <div>
                    <div className="text-2xl font-bold text-white">1,284</div>
                    <div className="text-xs text-muted-foreground">Leituras LPR</div>
                  </div>
                </div>

                <div className="rounded-xl bg-white/5 border border-white/10 p-4 flex flex-col justify-between">
                  <div className="h-8 w-8 rounded-lg bg-green-500/20 flex items-center justify-center text-green-500 mb-2"><Globe size={18}/></div>
                  <div>
                    <div className="text-2xl font-bold text-white">12</div>
                    <div className="text-xs text-muted-foreground">Locais Ativos</div>
                  </div>
                </div>
                
                <div className="col-span-3 h-16 rounded-xl bg-white/5 border border-white/10 flex items-center px-4 gap-4">
                   <div className="h-2 w-2 rounded-full bg-primary animate-pulse"/>
                   <div className="h-2 flex-1 rounded-full bg-white/10 overflow-hidden">
                      <div className="h-full w-[60%] bg-primary rounded-full"/>
                   </div>
                   <div className="text-xs text-muted-foreground font-mono">SYSTEM OPTIMAL</div>
                </div>
              </div>
            </div>
            
            {/* Glow effect behind mockup */}
            <div className="absolute inset-0 bg-primary/20 blur-3xl -z-10 transform translate-y-12 scale-90 rounded-full"></div>
          </motion.div>
        </div>
      </section>

      {/* --- Features Section --- */}
      <section className="py-32 px-6 relative">
        <div className="container max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <FadeInUp>
              <h2 className="text-3xl md:text-5xl font-bold mb-6">Stack Tecnológico Avançado</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
                Construído sobre uma arquitetura robusta de microsserviços para garantir escalabilidade infinita e segurança de nível empresarial.
              </p>
            </FadeInUp>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard 
              index={0}
              icon={ScanFace}
              title="Reconhecimento LPR"
              desc="Algoritmos de Deep Learning para detecção instantânea de placas veiculares, integrados diretamente ao feed de vídeo."
            />
            <FeatureCard 
              index={1}
              icon={Zap}
              title="Baixa Latência"
              desc="Streaming otimizado via WebRTC e HLS com MediaMTX, garantindo delay sub-segundo em qualquer rede."
            />
            <FeatureCard 
              index={2}
              icon={Globe}
              title="Cloud Nativo"
              desc="Acesse suas câmeras de qualquer lugar. Arquitetura Dockerizada pronta para AWS, Azure ou On-Premise."
            />
            <FeatureCard 
              index={3}
              icon={ShieldCheck}
              title="Segurança JWT"
              desc="Autenticação robusta com refresh tokens, proteção CSRF e controle de acesso baseado em funções (RBAC)."
            />
            <FeatureCard 
              index={4}
              icon={Cpu}
              title="Processamento Async"
              desc="Ingestão de dados massiva utilizando RabbitMQ e Celery para não bloquear a experiência do usuário."
            />
            <FeatureCard 
              index={5}
              icon={Video}
              title="Gestão Centralizada"
              desc="Dashboard intuitivo para adicionar, configurar e monitorar múltiplas câmeras RTSP simultaneamente."
            />
          </div>
        </div>
      </section>

      {/* --- Stats Section --- */}
      <section className="py-24 relative border-y border-white/5 bg-white/[0.02]">
        <div className="container max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
          {[
            { label: "Câmeras Suportadas", value: "∞" },
            { label: "Precisão IA", value: "99.8%" },
            { label: "Uptime SLA", value: "99.9%" },
            { label: "Latência Média", value: "<1s" },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, type: "spring" }}
              className="space-y-2"
            >
              <div className="text-5xl md:text-6xl font-bold text-white tracking-tighter">{stat.value}</div>
              <div className="text-sm font-medium text-primary uppercase tracking-widest">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* --- Footer CTA --- */}
      <section className="py-32 px-6 text-center relative overflow-hidden">
        <motion.div 
          className="absolute inset-0 opacity-20 bg-gradient-to-t from-primary/20 via-transparent to-transparent"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 0.2 }}
          transition={{ duration: 1.5 }}
        />
        
        <div className="relative z-10 container max-w-4xl mx-auto">
          <FadeInUp>
            <h2 className="text-4xl md:text-6xl font-bold mb-8 tracking-tight">Pronto para o futuro?</h2>
            <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
              Junte-se a empresas que transformaram sua segurança com a inteligência do GT-Vision.
            </p>
            <Button size="lg" className="h-16 px-12 text-xl rounded-full shadow-[0_0_40px_-10px_rgba(124,58,237,0.5)] hover:shadow-[0_0_60px_-10px_rgba(124,58,237,0.7)] transition-all duration-300 hover:scale-105" onClick={() => navigate('/login')}>
              Acessar Plataforma
            </Button>
          </FadeInUp>
        </div>
      </section>

      {/* --- Footer --- */}
      <footer className="py-8 border-t border-white/10 bg-black text-center text-sm text-muted-foreground/60">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center px-6">
          <p>&copy; {new Date().getFullYear()} GT-Vision VMS. All rights reserved.</p>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-white transition-colors">Privacidade</a>
            <a href="#" className="hover:text-white transition-colors">Termos</a>
            <a href="#" className="hover:text-white transition-colors">Contato</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;