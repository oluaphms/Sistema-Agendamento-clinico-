# 🚨 PREVENÇÃO DE ERROS DE SINCRONIZAÇÃO DO BANCO DE DADOS

## ❌ PROBLEMA IDENTIFICADO

**Erro:** `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) não existe essa coluna: paciente_1.categoria`

**Causa:** Desincronização entre os modelos SQLAlchemy definidos no código e a estrutura real das tabelas no banco de dados SQLite.

## 🔍 ANÁLISE DO PROBLEMA

### O que aconteceu:
1. **Modelo SQLAlchemy** definia a coluna `categoria` na tabela `paciente`
2. **Banco de dados real** não tinha essa coluna
3. **Query SQL** tentou acessar uma coluna inexistente
4. **Erro fatal** impediu o funcionamento da aplicação

### Tabelas afetadas:
- ✅ `paciente` - Faltavam colunas: `categoria`, `data_cadastro`, `ultima_atualizacao`
- ✅ `usuario` - Coluna extra: `usuario` (não crítica)
- ✅ Outras tabelas estavam sincronizadas

## 🛠️ SOLUÇÕES IMPLEMENTADAS

### 1. Script de Migração Imediata
```bash
python migrate_pacientes.py
```
- ✅ Adicionou colunas faltantes
- ✅ Atualizou registros existentes
- ✅ Criou backup automático

### 2. Verificação Automática na Inicialização
```python
# Adicionado ao app.py
def check_database_sync():
    """Verifica e corrige automaticamente problemas de sincronização"""
    # ... código de verificação e correção

# Executa automaticamente na inicialização
check_database_sync()
```

### 3. Script de Verificação Manual
```bash
python verify_database_sync.py
```
- 🔍 Verifica todas as tabelas
- 📋 Lista colunas faltantes
- ⚠️ Identifica problemas potenciais

## 🚀 PREVENÇÃO FUTURA

### ✅ ANTES DE IMPLEMENTAR NOVAS FUNCIONALIDADES:

1. **Sempre execute migração após alterar modelos:**
   ```bash
   python migrate_pacientes.py
   ```

2. **Verifique sincronização:**
   ```bash
   python verify_database_sync.py
   ```

3. **Teste a aplicação localmente antes de fazer deploy**

### ✅ AO ADICIONAR NOVAS COLUNAS:

1. **Crie script de migração específico**
2. **Teste em ambiente de desenvolvimento**
3. **Faça backup antes de migrar produção**
4. **Execute migração em horário de baixo tráfego**

### ✅ AO MODIFICAR MODELOS EXISTENTES:

1. **Verifique impacto nas queries existentes**
2. **Teste todas as funcionalidades relacionadas**
3. **Documente mudanças no banco**
4. **Atualize scripts de migração**

## 📋 CHECKLIST DE VERIFICAÇÃO

### Antes de cada deploy:
- [ ] Executar `python verify_database_sync.py`
- [ ] Verificar se não há erros de colunas faltantes
- [ ] Testar funcionalidades críticas (dashboard, pacientes, etc.)
- [ ] Fazer backup do banco se necessário

### Ao modificar modelos:
- [ ] Criar script de migração
- [ ] Testar em ambiente isolado
- [ ] Verificar compatibilidade com dados existentes
- [ ] Atualizar documentação

## 🔧 FERRAMENTAS DISPONÍVEIS

### Scripts de Manutenção:
1. **`migrate_pacientes.py`** - Migração específica da tabela paciente
2. **`verify_database_sync.py`** - Verificação completa de sincronização
3. **`database_sync_check.py`** - Verificação automática e correção
4. **`PREVENCAO_ERROS_BANCO.md`** - Esta documentação

### Comandos Úteis:
```bash
# Verificar estrutura atual
python -c "import sqlite3; conn = sqlite3.connect('instance/clinica.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(paciente)'); print([col[1] for col in cursor.fetchall()]); conn.close()"

# Verificar sincronização
python verify_database_sync.py

# Executar migração
python migrate_pacientes.py
```

## 🚨 EM CASO DE EMERGÊNCIA

### Se o erro voltar a acontecer:

1. **NÃO entre em pânico** - O sistema tem proteções automáticas
2. **Execute verificação:** `python verify_database_sync.py`
3. **Execute migração:** `python migrate_pacientes.py`
4. **Reinicie a aplicação**
5. **Verifique logs** para identificar causa raiz

### Contatos de Emergência:
- 📧 Documentar problema em issue do projeto
- 🔍 Analisar logs de erro
- 📋 Verificar se é problema de sincronização ou outro

## 📚 RECURSOS ADICIONAIS

### Documentação SQLAlchemy:
- [Migrations](https://docs.sqlalchemy.org/en/14/core/metadata.html#altering-schemas-through-migrations)
- [Database URLs](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)

### Boas Práticas:
- Sempre use migrations para alterações de schema
- Mantenha modelos e banco sincronizados
- Teste alterações em ambiente isolado
- Documente todas as mudanças

---

**⚠️ IMPORTANTE:** Este documento deve ser atualizado sempre que novas funcionalidades forem implementadas ou problemas similares forem identificados.

**🎯 OBJETIVO:** Garantir que o erro de sincronização NUNCA mais aconteça, através de prevenção automática e procedimentos claros de manutenção.
