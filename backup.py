import os, shutil, datetime
os.makedirs('backups', exist_ok=True)
ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
src = 'clinica.db'
dst = f'backups/clinica-{ts}.db'
if os.path.exists(src):
    shutil.copy2(src, dst)
    print('Backup criado:', dst)
else:
    print('Banco não encontrado:', src)
