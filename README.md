# Image Downloader

Script em Python para baixar imagens exibidas em uma página web utilizando Playwright.

## Funcionalidades

- Abre o site em um navegador.
- Permite navegar manualmente até a página desejada.
- Coleta todas as imagens (`<img>`) presentes na página.
- Baixa automaticamente os arquivos encontrados.
- Renomeia os arquivos utilizando o `alt` ou `title` da imagem.
- Remove acentos e caracteres especiais dos nomes.
- Evita sobrescrever arquivos duplicados.
- Salva tudo na pasta `downloads`.

## Requisitos

- Python 3.10 ou superior

## Instalação

Instale as dependências:

```bash
pip install playwright requests beautifulsoup4 unidecode
```

Instale o navegador utilizado pelo Playwright:

```bash
playwright install
```

## Como usar

Execute o script:

```bash
python baixar_imagens.py
```

Informe a URL desejada.

O navegador será aberto para que você possa navegar normalmente.

Quando a página estiver pronta, volte ao terminal e pressione **ENTER**.

As imagens encontradas serão baixadas automaticamente para a pasta:

```
downloads/
```

## Estrutura

```
.
├── baixar_imagens.py
├── downloads/
└── README.md
```

## Observações

- O script baixa apenas imagens presentes como elementos `<img>` na página no momento da captura.
- Algumas páginas podem carregar conteúdo dinamicamente ou exigir adaptações específicas.
- Utilize o script apenas em páginas cujo conteúdo você tenha permissão para acessar e baixar.

## Licença

Este projeto está disponível sob a licença MIT.