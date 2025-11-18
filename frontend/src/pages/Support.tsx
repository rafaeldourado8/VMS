import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send } from 'lucide-react';
import api from '@/lib/axios';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/use-toast';

interface Message {
  id: number;
  autor_id: number;
  autor_nome: string;
  conteudo: string;
  timestamp: string;
}

const Support = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuthStore();
  const { toast } = useToast();

  const fetchMessages = async () => {
    try {
      const response = await api.get('/support/chat/');
      const raw = response.data;
      // suporta array direto ou resposta paginada { results: [...] }
      const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);
      setMessages(list);
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error);
      toast({
        title: 'Erro ao carregar mensagens',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000); // Poll a cada 5s
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [toast]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await api.post('/support/chat/', { conteudo: newMessage });
      setNewMessage('');
      // buscar novas mensagens (ou você pode optar por inserir a mensagem retornada)
      fetchMessages();
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      toast({
        title: 'Erro ao enviar mensagem',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground">Suporte</h1>
        <p className="text-muted-foreground">Chat com a equipe de suporte</p>
      </div>

      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle>Mensagens</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.map((message) => {
              const isOwn = message.autor_id === user?.id;
              return (
                <div
                  key={message.id}
                  className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg px-4 py-2 ${
                      isOwn
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-foreground'
                    }`}
                  >
                    <div className="text-xs opacity-70 mb-1">
                      {message.autor_nome}
                    </div>
                    <div>{message.conteudo}</div>
                    <div className="text-xs opacity-70 mt-1">
                      {new Date(message.timestamp).toLocaleString('pt-BR')}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSend} className="flex gap-2">
            <Input
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Digite sua mensagem..."
            />
            <Button type="submit" size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Support;