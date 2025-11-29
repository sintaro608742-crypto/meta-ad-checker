import type { ReactNode } from 'react';
import { Box, AppBar, Toolbar, Typography, Container, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

interface PublicLayoutProps {
  children: ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  showBackground?: boolean;
}

export const PublicLayout = ({
  children,
  maxWidth = 'lg',
  showBackground = true
}: PublicLayoutProps) => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: showBackground
          ? 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)'
          : 'transparent',
      }}
    >
      {/* ヘッダー */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: showBackground ? 'rgba(255, 255, 255, 0.1)' : 'primary.main',
          backdropFilter: showBackground ? 'blur(10px)' : 'none',
        }}
      >
        <Toolbar>
          <CheckCircleOutlineIcon sx={{ mr: 1, color: 'white' }} />
          <Typography
            variant="h6"
            sx={{
              flexGrow: 1,
              color: 'white',
              fontWeight: 700,
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          >
            メタ広告審査チェッカー
          </Typography>
          <Button
            color="inherit"
            startIcon={<HelpOutlineIcon />}
            onClick={() => navigate('/guide')}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            使い方ガイド
          </Button>
        </Toolbar>
      </AppBar>

      {/* メインコンテンツ */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          py: 4,
        }}
      >
        <Container maxWidth={maxWidth} sx={{ flexGrow: 1 }}>
          {children}
        </Container>
      </Box>

      {/* フッター */}
      <Box
        component="footer"
        sx={{
          py: 3,
          textAlign: 'center',
          color: showBackground ? 'white' : 'text.secondary',
          backgroundColor: showBackground ? 'rgba(0, 0, 0, 0.1)' : 'transparent',
        }}
      >
        <Typography variant="body2">
          © 2025 メタ広告審査チェッカー. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};
