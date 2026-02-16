import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Plus, Trash2, Edit2 } from 'lucide-react'

interface RetentionPlan {
  id: number
  name: string
  days: number
  description: string
  is_active: boolean
  created_at: string
}

export default function RetentionPlansPage() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingPlan, setEditingPlan] = useState<RetentionPlan | null>(null)

  const { data: plans = [], isLoading } = useQuery<RetentionPlan[]>({
    queryKey: ['retention-plans'],
    queryFn: async () => {
      const response = await axios.get('/api/timeline/retention-plans/')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await axios.delete(`/api/timeline/retention-plans/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['retention-plans'] })
    },
  })

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Planos de Retenção</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Configure os planos de gravação cíclica
          </p>
        </div>
        <button
          onClick={() => {
            setEditingPlan(null)
            setIsModalOpen(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <Plus className="w-4 h-4" />
          Novo Plano
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {plans.map(plan => (
            <div
              key={plan.id}
              className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{plan.name}</h3>
                  <p className="text-2xl font-bold text-blue-500">{plan.days} dias</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setEditingPlan(plan)
                      setIsModalOpen(true)
                    }}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(plan.id)}
                    className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 text-red-500 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {plan.description}
              </p>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <span className={`text-xs px-2 py-1 rounded ${
                  plan.is_active 
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {plan.is_active ? 'Ativo' : 'Inativo'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <RetentionPlanModal
          plan={editingPlan}
          onClose={() => setIsModalOpen(false)}
        />
      )}
    </div>
  )
}

function RetentionPlanModal({ plan, onClose }: { plan: RetentionPlan | null; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    name: plan?.name || '',
    days: plan?.days || 7,
    description: plan?.description || '',
    is_active: plan?.is_active ?? true,
  })

  const saveMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      if (plan) {
        await axios.put(`/api/timeline/retention-plans/${plan.id}/`, data)
      } else {
        await axios.post('/api/timeline/retention-plans/', data)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['retention-plans'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">
          {plan ? 'Editar Plano' : 'Novo Plano'}
        </h2>
        
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
            <label className="block text-sm font-medium mb-1">Dias de Retenção</label>
            <input
              type="number"
              value={formData.days}
              onChange={(e) => setFormData(f => ({ ...f, days: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
              min={1}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Descrição</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700"
              rows={3}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData(f => ({ ...f, is_active: e.target.checked }))}
              className="w-4 h-4"
            />
            <label className="text-sm">Plano ativo</label>
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
