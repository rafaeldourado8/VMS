# Correções de Segurança e Acessibilidade

## ✅ Problemas Resolvidos

### 1. Content Security Policy (CSP) - 'unsafe-eval'

**Problema**: CSP permitia `'unsafe-eval'` que pode facilitar ataques XSS.

**Solução**: Removido `'unsafe-eval'` do CSP em `index.html`.

**Justificativa**: 
- HLS.js v1.5.7 não requer `eval()` por padrão
- A biblioteca usa Web Workers que não necessitam de eval
- Mantém `'unsafe-inline'` apenas para scripts inline necessários (Google Maps)

**CSP Atualizado**:
```html
<meta http-equiv="Content-Security-Policy" 
  content="default-src 'self'; 
           script-src 'self' 'unsafe-inline' https://maps.googleapis.com; 
           style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
           font-src 'self' https://fonts.gstatic.com; 
           connect-src 'self' http: https: ws: wss:; 
           media-src 'self' http: https: blob: data:; 
           img-src 'self' http: https: data: blob:;" />
```

### 2. Acessibilidade - Botão sem Label

**Problema**: Botão de toggle de senha sem atributo `aria-label`.

**Solução**: Adicionado `aria-label` dinâmico em `LoginPage.tsx`.

**Código**:
```tsx
<button
  type="button"
  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
  className="..."
  onClick={() => setShowPassword(!showPassword)}
>
  {showPassword ? <EyeOff /> : <Eye />}
</button>
```

## 🔒 Melhorias de Segurança

### CSP Mais Restritivo
- ❌ Removido `'unsafe-eval'`
- ✅ Mantido `'unsafe-inline'` apenas onde necessário
- ✅ Whitelist específica para domínios externos (Google)

### Benefícios
1. **Proteção contra XSS**: Impede execução de código arbitrário
2. **Conformidade**: Atende padrões de segurança modernos
3. **Performance**: Sem overhead de eval()

## ♿ Melhorias de Acessibilidade

### ARIA Labels
- ✅ Botões interativos com labels descritivos
- ✅ Suporte para leitores de tela
- ✅ Conformidade WCAG 2.1

## 🧪 Testes

Para verificar as correções:

1. **CSP**: Abra DevTools → Console
   - Não deve haver erros de CSP
   - HLS.js deve funcionar normalmente

2. **Acessibilidade**: Use leitor de tela
   - Botão de senha deve anunciar "Mostrar senha" ou "Ocultar senha"

## 📝 Notas

- Se precisar de `eval()` no futuro, considere usar Web Workers
- Para scripts inline, use nonces ou hashes no CSP
- Mantenha bibliotecas atualizadas para evitar vulnerabilidades
