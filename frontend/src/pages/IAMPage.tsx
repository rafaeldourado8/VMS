import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Users, Shield, FileText, Plus, Edit2, Trash2, Key } from 'lucide-react'

interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'operator' | 'viewer'
  is_active: boolean
  permissions: string[]
  created_at: string
}

interface Permission {
  id: string
  name: string
  description: string
  resource: string
}

interface Rule {
  id: number
  name: string
  description: string
  conditions: Record<string, any>
  actions: string[]
  is_active: boolean
}

export default function IAMPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'permissions' | 'rules'>('users')

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Gerenciamento de Acesso (IAM)</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Gerencie usuários, permissões e regras de acesso
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            activeTab === 'users'
              ? 'border-blue-500 text-blue-500'
              : 'border-transparent text-gray-600 dark:text-gray-400'
          }`}
        >
          <Users className="w-4 h-4" />
          Usuários
        </button>
        <button
          onClick={() => setActiveTab('permissions')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            activeTab === 'permissions'
              ? 'border-blue-500 text-blue-500'
              : 'border-transparent text-gray-600 dark:text-gray-400'
          }`}
        >
          <Shield className="w-4 h-4" />
          Permissões
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
            activeTab === 'rules'
              ? 'border-blue-500 text-blue-500'
              : 'border-transparent text-gray-600 dark:text-gray-400'
          }`}
        >
          <FileText className="w-4 h-4" />
          Regras
        </button>
      </div>

      {/* Content */}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'permissions' && <PermissionsTab />}
      {activeTab === 'rules' && <RulesTab />}
    </div>
  )
}

function UsersTab() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const { data: users = [], isLoading } = useQuery<User[]>({
    queryKey: ['iam-users'],
    queryFn: async () => {
      const response = await axios.get('/api/iam/users/')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/iam/users/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iam-users'] })
    },
  })

  const roleColors = {
    admin: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400',
    operator: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400',
    viewer: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400',
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          onClick={() => {
            setEditingUser(null)
            setIsModalOpen(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <Plus className="w-4 h-4" />
          Novo Usuário
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permissões</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {users.map(user => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">{user.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-xs px-2 py-1 rounded ${roleColors[user.role]}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-xs px-2 py-1 rounded ${
                      user.is_active
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {user.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {user.permissions?.slice(0, 3).map(perm => (
                        <span key={perm} className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">
                          {perm}
                        </span>
                      ))}
                      {user.permissions?.length > 3 && (
                        <span className="text-xs text-gray-500">+{user.permissions.length - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button
                      onClick={() => {
                        setEditingUser(user)
                        setIsModalOpen(true)
                      }}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded inline-flex"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(user.id)}
                      className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-500 rounded inline-flex ml-2"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isModalOpen && <UserModal user={editingUser} onClose={() => setIsModalOpen(false)} />}
    </div>
  )
}

function PermissionsTab() {
  const permissions: Permission[] = [
    { id: 'cameras.view', name: 'Visualizar Câmeras', description: 'Ver lista e streams de câmeras', resource: 'cameras' },
    { id: 'cameras.create', name: 'Criar Câmeras', description: 'Adicionar novas câmeras', resource: 'cameras' },
    { id: 'cameras.edit', name: 'Editar Câmeras', description: 'Modificar configurações de câmeras', resource: 'cameras' },
    { id: 'cameras.delete', name: 'Deletar Câmeras', description: 'Remover câmeras do sistema', resource: 'cameras' },
    { id: 'recordings.view', name: 'Visualizar Gravações', description: 'Acessar gravações', resource: 'recordings' },
    { id: 'recordings.download', name: 'Baixar Gravações', description: 'Download de arquivos de gravação', resource: 'recordings' },
    { id: 'recordings.delete', name: 'Deletar Gravações', description: 'Remover gravações', resource: 'recordings' },
    { id: 'detections.view', name: 'Visualizar Detecções', description: 'Ver detecções de LPR', resource: 'detections' },
    { id: 'users.manage', name: 'Gerenciar Usuários', description: 'CRUD de usuários', resource: 'users' },
    { id: 'settings.manage', name: 'Gerenciar Configurações', description: 'Alterar configurações do sistema', resource: 'settings' },
  ]

  const groupedPermissions = permissions.reduce((acc, perm) => {
    if (!acc[perm.resource]) acc[perm.resource] = []
    acc[perm.resource].push(perm)
    return acc
  }, {} as Record<string, Permission[]>)

  return (
    <div className="space-y-6">
      {Object.entries(groupedPermissions).map(([resource, perms]) => (
        <div key={resource} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4 capitalize">{resource}</h3>
          <div className="space-y-3">
            {perms.map(perm => (
              <div key={perm.id} className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded">
                <Key className="w-5 h-5 text-blue-500 mt-0.5" />
                <div className="flex-1">
                  <div className="font-medium">{perm.name}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{perm.description}</div>
                  <div className="text-xs text-gray-500 mt-1 font-mono">{perm.id}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function RulesTab() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<Rule | null>(null)

  const { data: rules = [], isLoading } = useQuery<Rule[]>({
    queryKey: ['iam-rules'],
    queryFn: async () => {
      const response = await axios.get('/api/iam/rules/')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/iam/rules/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iam-rules'] })
    },
  })

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          onClick={() => {
            setEditingRule(null)
            setIsModalOpen(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <Plus className="w-4 h-4" />
          Nova Regra
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="grid gap-4">
          {rules.map(rule => (
            <div key={rule.id} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{rule.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{rule.description}</p>
                </div>
                <div className="flex gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    rule.is_active
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                  }`}>
                    {rule.is_active ? 'Ativa' : 'Inativa'}
                  </span>
                  <button
                    onClick={() => {
                      setEditingRule(rule)
                      setIsModalOpen(true)
                    }}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(rule.id)}
                    className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-500 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <div>
                  <span className="text-xs font-medium text-gray-500">Condições:</span>
                  <pre className="text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(rule.conditions, null, 2)}
                  </pre>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">Ações:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {rule.actions.map(action => (
                      <span key={action} className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded">
                        {action}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isModalOpen && <RuleModal rule={editingRule} onClose={() => setIsModalOpen(false)} />}
    </div>
  )
}

function UserModal({ user, onClose }: { user: User | null; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    password: '',
    role: user?.role || 'viewer',
    is_active: user?.is_active ?? true,
    permissions: user?.permissions || [],
  })

  const saveMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      if (user) {
        await axios.put(`/api/iam/users/${user.id}/`, data)
      } else {
        await axios.post('/api/iam/users/', data)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iam-users'] })
      onClose()
    },
  })

  const availablePermissions = [
    'cameras.view', 'cameras.create', 'cameras.edit', 'cameras.delete',
    'recordings.view', 'recordings.download', 'recordings.delete',
    'detections.view', 'users.manage', 'settings.manage'
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">{user ? 'Editar Usuário' : 'Novo Usuário'}</h2>
        
        <form onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(formData) }} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nome</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(f => ({ ...f, email: e.target.value }))}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
                required
              />
            </div>
          </div>

          {!user && (
            <div>
              <label className="block text-sm font-medium mb-1">Senha</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData(f => ({ ...f, password: e.target.value }))}
                className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
                required={!user}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData(f => ({ ...f, role: e.target.value as any }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
            >
              <option value="viewer">Viewer</option>
              <option value="operator">Operator</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Permissões</label>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto p-3 border rounded-lg dark:border-gray-700">
              {availablePermissions.map(perm => (
                <label key={perm} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={formData.permissions.includes(perm)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData(f => ({ ...f, permissions: [...f.permissions, perm] }))
                      } else {
                        setFormData(f => ({ ...f, permissions: f.permissions.filter(p => p !== perm) }))
                      }
                    }}
                    className="w-4 h-4"
                  />
                  {perm}
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData(f => ({ ...f, is_active: e.target.checked }))}
              className="w-4 h-4"
            />
            <label className="text-sm">Usuário ativo</label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {saveMutation.isPending ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function RuleModal({ rule, onClose }: { rule: Rule | null; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: rule?.name || '',
    description: rule?.description || '',
    conditions: JSON.stringify(rule?.conditions || { role: 'viewer', resource: 'cameras' }, null, 2),
    actions: rule?.actions?.join(', ') || 'allow',
    is_active: rule?.is_active ?? true,
  })

  const saveMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const payload = {
        ...data,
        conditions: JSON.parse(data.conditions),
        actions: data.actions.split(',').map(a => a.trim()),
      }
      if (rule) {
        await axios.put(`/api/iam/rules/${rule.id}/`, payload)
      } else {
        await axios.post('/api/iam/rules/', payload)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iam-rules'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl">
        <h2 className="text-xl font-bold mb-4">{rule ? 'Editar Regra' : 'Nova Regra'}</h2>
        
        <form onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(formData) }} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Nome</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Descrição</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Condições (JSON)</label>
            <textarea
              value={formData.conditions}
              onChange={(e) => setFormData(f => ({ ...f, conditions: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 font-mono text-sm"
              rows={6}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Ações (separadas por vírgula)</label>
            <input
              type="text"
              value={formData.actions}
              onChange={(e) => setFormData(f => ({ ...f, actions: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
              placeholder="allow, deny, log"
              required
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData(f => ({ ...f, is_active: e.target.checked }))}
              className="w-4 h-4"
            />
            <label className="text-sm">Regra ativa</label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {saveMutation.isPending ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
