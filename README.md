
# Gaza Casualties Dashboard

*A real-time dashboard tracking the loss of life in Palestine (Gaza and West Bank) since October 7, 2023, built with Python Dash and Plotly.*

---

## 🌟 Features

- **Real-time Data**: Automatically fetches updated casualty data every 24 hours  
- **Interactive Visualizations**: Time-series charts with date range filtering  
- **Key Performance Indicators**: Live KPI cards showing totals and 7-day changes  
- **Responsive Design**: Mobile-friendly interface with Palestinian flag color scheme  
- **Data Reliability**: Dual data source fallback (CSV primary, JSON backup)

---

## 📊 Demo

The dashboard displays:

- Total killed and injured civilians  
- Children and women casualties specifically  
- 7-day trend indicators (▲/▼) for each metric  
- Interactive time-series charts with date range selection

---

## 🛠 Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Local Setup

```bash
git clone https://github.com/yourusername/gaza-dashboard.git
cd gaza-dashboard
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create assets directory:
```bash
mkdir assets
mv styles.css assets/
```

Run the application:
```bash
python app.py
```

Open in browser: http://127.0.0.1:8050

---

## 🚀 Deployment

### Render.com (Recommended)

1. Fork this repository to your GitHub account
2. Go to [render.com](https://render.com) and sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repository

Configure deployment:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:server`
- Environment: Python 3

Add to `app.py`:
```python
server = app.server  # Expose Flask server for WSGI
```

### Heroku

Install Heroku CLI and login:
```bash
heroku login
```

Create Heroku app:
```bash
heroku create your-gaza-dashboard
```

Add `Procfile`:
```
web: gunicorn app:server
```

Deploy:
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Railway

- Connect GitHub at [railway.app](https://railway.app)
- Deploy from GitHub - select your forked repository
- Configure start command: `gunicorn app:server`

---

## 🧠 Data Sources

- Primary: CSV API endpoint (Tech for Palestine)
- Fallback: JSON from GitHub repository
- Update Frequency: Every 24 hours per user session
- Local Caching: Daily cached files in `data/raw/`

---

## 🗂 Project Structure

```
gaza-dashboard/
├── app.py              # Main Dash application
├── fetch_data.py       # Data fetching and caching logic
├── requirements.txt    # Python dependencies
├── assets/
│   └── styles.css     # Custom CSS styling
├── data/
│   └── raw/           # Cached data files (auto-created)
└── README.md          # This file
```

---

## ⚙️ Configuration

### Environment Variables

- `PORT`: Server port (default: 8050 locally, auto-set on platforms)
- `DEBUG`: Set to False for production

### Customization

- **Colors**: Modify CSS variables in `assets/styles.css`
- **Update Interval**: Change interval value in `dcc.Interval` component
- **Data Window**: Adjust `WINDOW` variable for trend calculations

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📢 Data Disclaimer

This dashboard presents data as provided by Tech for Palestine and other humanitarian sources. The metrics displayed do not fully reflect the complete scope of loss of human life in Palestine. For comprehensive reporting, please consult multiple humanitarian organizations and official sources.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Data Source**: Tech for Palestine  
- **Built with**: Dash, Plotly, Pandas  
- **Styling**: Palestinian flag color scheme  

---

## 🆘 Support

If you encounter issues:

- Check the Issues page
- Ensure all dependencies are installed correctly
- Verify data sources are accessible
- Check server logs for deployment issues

---

> "We must never forget that behind every statistic is a human life, a story, a family."
