# Interest Rate Swap Analyzer - Web App

This is a client-side web application version of the Interest Rate Swap Analyzer.

## Features

- **Zero dependencies**: Runs entirely in your browser
- **No backend required**: All calculations done client-side
- **Instant updates**: Results update as you change inputs
- **Mobile responsive**: Works on all devices
- **Privacy-first**: Your data never leaves your browser

## How It Works

The web app is a direct port of the Python implementation to vanilla JavaScript. It includes:

- All calculation logic from the Python package
- Interactive input forms with real-time updates
- Formatted tables displaying analysis results
- Responsive design using Tailwind CSS

## Technology Stack

- **Vanilla JavaScript** - No frameworks, just pure JS
- **HTML5** - Semantic markup
- **Tailwind CSS** - Utility-first CSS via CDN
- **GitHub Pages** - Free static hosting

## Local Development

Simply open `index.html` in your browser:

```bash
cd docs
open index.html  # macOS
# or
start index.html  # Windows
# or
xdg-open index.html  # Linux
```

Or use a simple HTTP server:

```bash
python -m http.server 8000
# Then visit http://localhost:8000
```

## Deployment

This site is automatically deployed to GitHub Pages from the `/docs` folder on the main branch.

## Calculations

All calculations match the Python implementation exactly:

- Comparative advantage analysis
- Total arbitrage opportunity
- Party positions and benefits
- Market improvement calculations

## License

MIT License
