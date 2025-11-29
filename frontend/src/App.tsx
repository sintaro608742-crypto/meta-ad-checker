import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AdCheckerPage } from './pages/AdCheckerPage';
import { GuidePage } from './pages/GuidePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* P-001: メタ広告審査チェッカー（メインページ） */}
        <Route path="/" element={<AdCheckerPage />} />

        {/* P-002: 使い方ガイド / FAQ */}
        <Route path="/guide" element={<GuidePage />} />

        {/* 404: 存在しないパスはトップページへリダイレクト */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
