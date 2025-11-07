# Fastrax Price Change

A fullstack application for managing product price changes, built with Flask (Python) for the backend and React (TypeScript) for the frontend.

## Features

- Upload and process product price change PDFs
- Manage products and prices in a SQLite database
- Export updated product lists to CSV
- User authentication (Fastrax login)
- Modern React frontend with live preview

## Project Structure

```
Fastrax-Price-Change/
├── backend/
│   ├── src/
│   │   ├── main.py           # Flask app entry point
│   │   ├── app.py            # Flask app and SQLAlchemy setup
│   │   ├── database.py       # Database logic (sqlite3/SQLAlchemy)
│   │   ├── PDFextractor.py   # PDF parsing logic
│   │   ├── CSVwriter.py      # CSV export logic
│   │   ├── ...
│   ├── csv/                  # CSV files
│   ├── database/             # SQLite DB
│   ├── drivers/              # Selenium drivers
│   ├── requirements.txt      # Python dependencies
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React app
│   │   ├── pages/            # React pages
│   │   ├── Components/       # React components
│   ├── package.json          # Frontend dependencies
│   └── ...
├── run_all.py                # Script to run backend & frontend together
├── run_all.bat               # Windows batch script to run both
└── README.md                 # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js (v18+ recommended)
- npm (comes with Node.js)

### Backend Setup

1. **Install BACKEND dependencies**
   ```sh
   pip install -r requirements.txt
   ```
2. **Run the backend**
   ```sh
   python backend/src/main.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```sh
   cd frontend
   npm install
   ```
2. **Run the frontend**
   ```sh
   npm run dev
   ```

### Run Both Together

- **Python script:**
  ```sh
  python run_all.py
  ```
- **Batch script (Windows):**
  ```cmd
  run_all.bat
  ```

## Database

- SQLite database is stored in `backend/src/instance/products.db`.
- If you encounter `database is locked` errors, ensure all connections are properly closed and avoid simultaneous writes.

## PDF & CSV

- Upload PDFs via the frontend to update product prices.
- Export updated product lists as CSV from the backend.

## Environment Variables

- See `backend/src/.env.example` for required variables.

## Contributing

1. Fork the repo and create your feature branch (`git checkout -b feature/YourFeature`)
2. Commit your changes (`git commit -am 'Add some feature'`)
3. Push to the branch (`git push origin feature/YourFeature`)
4. Open a Pull Request

## License

MIT License
