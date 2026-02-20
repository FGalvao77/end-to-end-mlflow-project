from platform import platform, python_version

# Teste simples para verificar o ambiente de execução
def test_environment():
    print(f'\nPlatform: {platform()}')
    print(f'Python version: {python_version()}\n')

# Executar o teste de ambiente quando este script for executado diretamente
if __name__ == '__main__':
    test_environment()