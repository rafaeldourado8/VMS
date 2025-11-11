import { NavLink } from '@/components/NavLink';
import { useAuthStore } from '@/store/authStore';
import { 
  LayoutDashboard, 
  Video, 
  FileSearch, 
  Settings, 
  Users, 
  HelpCircle, 
  LogOut,
  Camera,
  ChevronDown
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

const Sidebar = () => {
  const { user, logout } = useAuthStore();
  const [isManagementOpen, setIsManagementOpen] = useState(false);

  const navItems = [
    { title: 'Dashboard', path: '/', icon: LayoutDashboard },
    { title: 'Câmeras ao Vivo', path: '/live', icon: Video },
    { title: 'Detecções LPR', path: '/detections', icon: FileSearch },
  ];

  const managementItems = [
    { title: 'Câmeras', path: '/admin/cameras', icon: Camera },
    ...(user?.role === 'admin' ? [{ title: 'Usuários', path: '/admin/users', icon: Users }] : []),
  ];

  return (
    <aside className="w-64 h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sidebar-primary rounded-lg">
            <Video className="h-6 w-6 text-sidebar-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-sidebar-foreground">GT-Vision</h1>
            <p className="text-xs text-sidebar-foreground/70">{user?.name || 'Usuário'}</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
            activeClassName="bg-sidebar-accent text-sidebar-foreground font-medium"
          >
            <item.icon className="h-5 w-5" />
            <span>{item.title}</span>
          </NavLink>
        ))}

        {/* Management Section */}
        <div className="pt-2">
          <button
            onClick={() => setIsManagementOpen(!isManagementOpen)}
            className="w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
          >
            <div className="flex items-center gap-3">
              <Settings className="h-5 w-5" />
              <span>Gerenciamento</span>
            </div>
            <ChevronDown className={cn("h-4 w-4 transition-transform", isManagementOpen && "rotate-180")} />
          </button>
          
          {isManagementOpen && (
            <div className="ml-4 mt-1 space-y-1">
              {managementItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
                  activeClassName="bg-sidebar-accent text-sidebar-foreground font-medium"
                >
                  <item.icon className="h-4 w-4" />
                  <span className="text-sm">{item.title}</span>
                </NavLink>
              ))}
            </div>
          )}
        </div>

        <NavLink
          to="/support"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
          activeClassName="bg-sidebar-accent text-sidebar-foreground font-medium"
        >
          <HelpCircle className="h-5 w-5" />
          <span>Suporte</span>
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground transition-colors"
        >
          <LogOut className="h-5 w-5" />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
