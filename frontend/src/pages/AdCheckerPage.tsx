import { useCallback, useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  LinearProgress,
} from '@mui/material';
import { apiClient } from '../services/ApiClient';
import { useDropzone } from 'react-dropzone';
import { PublicLayout } from '../layouts/PublicLayout';
import { useAdChecker } from '../hooks/useAdChecker';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import { EnhancedRecommendations } from '../components/EnhancedRecommendations';

export const AdCheckerPage = () => {
  // バックエンドの起動状態管理
  const [backendStatus, setBackendStatus] = useState<'checking' | 'ready' | 'error'>('checking');

  // ページロード時にバックエンドを起動
  useEffect(() => {
    const wakeUpBackend = async () => {
      setBackendStatus('checking');
      const isReady = await apiClient.waitForBackend(1, 0); // 1回のヘルスチェック（90秒タイムアウト）
      setBackendStatus(isReady ? 'ready' : 'error');
    };
    wakeUpBackend();
  }, []);

  const {
    formData,
    imagePreview,
    checkState,
    result,
    hasInput,
    updateField,
    handleImageUpload,
    clearImage,
    checkAdvertisement,
    resetForm,
  } = useAdChecker();

  // Dropzone設定
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        handleImageUpload(acceptedFiles[0]).catch(() => {
          // エラーはuseAdChecker内でハンドリング済み
        });
      }
    },
    [handleImageUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 20 * 1024 * 1024, // 20MB
    multiple: false,
  });

  // ステータスバッジの表示
  const getStatusBadge = () => {
    if (!result) return null;

    const statusConfig = {
      approved: {
        label: '承認される可能性が高い',
        color: 'success' as const,
        icon: <CheckCircleIcon />,
      },
      needs_review: {
        label: '要審査',
        color: 'warning' as const,
        icon: <WarningIcon />,
      },
      rejected: {
        label: '却下される可能性が高い',
        color: 'error' as const,
        icon: <ErrorIcon />,
      },
    };

    const config = statusConfig[result.status];

    return (
      <Chip
        label={config.label}
        color={config.color}
        icon={config.icon}
        sx={{
          mt: 2,
          fontSize: '0.875rem',
          fontWeight: 700,
          px: 2,
          py: 3,
        }}
      />
    );
  };

  return (
    <PublicLayout maxWidth="lg" showBackground={false}>
      {/* バックエンド起動中の表示 */}
      {backendStatus === 'checking' && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 9999,
            bgcolor: '#059669',
            color: 'white',
            py: 1.5,
            px: 2,
            textAlign: 'center',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
            <CircularProgress size={20} sx={{ color: 'white' }} />
            <Typography sx={{ fontWeight: 600 }}>
              サーバーを準備中です...（初回は最大1分ほどかかる場合があります）
            </Typography>
          </Box>
          <LinearProgress
            sx={{
              mt: 1,
              bgcolor: 'rgba(255,255,255,0.3)',
              '& .MuiLinearProgress-bar': { bgcolor: 'white' },
            }}
          />
        </Box>
      )}

      <Box
        sx={{
          py: 6,
          px: 3,
          pt: backendStatus === 'checking' ? 12 : 6, // 起動中はパディング追加
          background: 'linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 50%, #e0f2fe 100%)',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        {/* タイトル */}
        <Typography
          variant="h2"
          component="h1"
          sx={{
            fontSize: { xs: '2.5rem', md: '3.5rem' },
            fontWeight: 800,
            mb: 2,
            background: 'linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textAlign: 'center',
          }}
        >
          メタ広告審査チェッカー
        </Typography>

        {/* 広告テキスト入力 */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            borderRadius: 4,
            mb: 3,
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
          }}
        >
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
            広告テキスト
          </Typography>

          <Stack spacing={3}>
            <TextField
              fullWidth
              label="見出し（任意）"
              placeholder="例: 今すぐダウンロード"
              value={formData.headline}
              onChange={(e) => updateField('headline', e.target.value)}
              inputProps={{ maxLength: 255 }}
            />

            <TextField
              fullWidth
              multiline
              rows={4}
              label="説明文（任意）"
              placeholder="例: 業界最安値で高品質なサービスを提供します"
              value={formData.description}
              onChange={(e) => updateField('description', e.target.value)}
              inputProps={{ maxLength: 2000 }}
            />

            <TextField
              fullWidth
              label="CTA（任意）"
              placeholder="例: 詳細を見る"
              value={formData.cta}
              onChange={(e) => updateField('cta', e.target.value)}
              inputProps={{ maxLength: 30 }}
            />
          </Stack>
        </Paper>

        {/* 画像アップロード */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            borderRadius: 4,
            mb: 3,
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
          }}
        >
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
            広告画像（任意）
          </Typography>

          <Box
            {...getRootProps()}
            sx={{
              border: '3px dashed',
              borderColor: isDragActive ? 'primary.main' : '#10b981',
              borderRadius: 4,
              p: 6,
              textAlign: 'center',
              background: isDragActive
                ? 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)'
                : 'linear-gradient(135deg, #f0fdfa 0%, #ecfdf5 100%)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)',
                borderColor: '#059669',
                transform: 'scale(1.02)',
              },
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 64, color: '#10b981', mb: 2 }} />
            <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
              画像をドラッグ&ドロップ
            </Typography>
            <Typography variant="body2" color="text.secondary">
              または、クリックしてファイルを選択（最大20MB、JPEG/PNG/WebP/PDF）
            </Typography>
          </Box>

          {/* 画像プレビュー */}
          {imagePreview && (
            <Box
              sx={{
                mt: 3,
                maxWidth: 400,
                mx: 'auto',
                borderRadius: 3,
                overflow: 'hidden',
                boxShadow: 3,
                position: 'relative',
              }}
            >
              <img
                src={imagePreview.previewUrl}
                alt="プレビュー"
                style={{ width: '100%', height: 'auto', display: 'block' }}
              />
              <IconButton
                onClick={(e) => {
                  e.stopPropagation();
                  clearImage();
                }}
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 1)' },
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          )}
        </Paper>

        {/* URL審査 */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            borderRadius: 4,
            mb: 3,
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
          }}
        >
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            <LinkIcon sx={{ color: '#10b981' }} />
            URL審査（任意）
          </Typography>

          <TextField
            fullWidth
            label="LP・広告ページのURL"
            placeholder="例: https://example.com/landing-page"
            value={formData.pageUrl}
            onChange={(e) => updateField('pageUrl', e.target.value)}
            helperText="URLを入力すると、ページのOGP画像とテキストを自動取得して審査します"
            InputProps={{
              startAdornment: (
                <Box sx={{ mr: 1, display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                  <LinkIcon fontSize="small" />
                </Box>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&:hover fieldset': {
                  borderColor: '#10b981',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#059669',
                },
              },
            }}
          />
        </Paper>

        {/* チェック実行ボタン */}
        <Paper elevation={2} sx={{ p: 4, borderRadius: 4, mb: 3 }}>
          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={checkAdvertisement}
            disabled={checkState.isLoading || !hasInput}
            startIcon={checkState.isLoading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            sx={{
              py: 2.5,
              fontSize: '1.125rem',
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 20px rgba(16, 185, 129, 0.4)',
              },
            }}
          >
            {checkState.isLoading ? '審査チェック中...' : 'AIチェック実行'}
          </Button>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ textAlign: 'center', mt: 1.5 }}
          >
            ※テキスト、画像、またはURLの少なくとも1つが必要です
          </Typography>

          {/* エラー表示 */}
          {checkState.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {checkState.error}
            </Alert>
          )}
        </Paper>

        {/* 結果表示エリア */}
        {checkState.hasResult && result && (
          <>
            {/* 総合スコア */}
            <Paper
              elevation={2}
              sx={{
                p: 4,
                borderRadius: 4,
                mb: 3,
                animation: 'fadeInUp 0.8s ease-out',
                '@keyframes fadeInUp': {
                  from: { opacity: 0, transform: 'translateY(20px)' },
                  to: { opacity: 1, transform: 'translateY(0)' },
                },
              }}
            >
              <Box
                sx={{
                  textAlign: 'center',
                  p: 6,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%)',
                  borderRadius: 5,
                  color: 'white',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <Typography
                  variant="h1"
                  sx={{
                    fontSize: { xs: '4rem', md: '5rem' },
                    fontWeight: 800,
                    mb: 1,
                    textShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                  }}
                >
                  {result.overall_score}%
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  総合審査スコア
                </Typography>
                {getStatusBadge()}
              </Box>
            </Paper>

            {/* 問題箇所の指摘 */}
            {result.violations.length > 0 && (
              <Paper elevation={2} sx={{ p: 4, borderRadius: 4, mb: 3 }}>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
                  問題箇所の指摘
                </Typography>
                <Stack spacing={2}>
                  {result.violations.map((violation, index) => (
                    <Box
                      key={index}
                      sx={{
                        background: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
                        borderLeft: '5px solid #ef4444',
                        p: 2.5,
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          transform: 'translateX(4px)',
                          boxShadow: '0 4px 12px rgba(239, 68, 68, 0.15)',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        <Typography
                          variant="body1"
                          sx={{ fontWeight: 700, color: '#dc2626', flex: 1 }}
                        >
                          {violation.category === 'text_overlay' && '画像内テキスト量'}
                          {violation.category === 'prohibited_content' && '禁止コンテンツ'}
                          {violation.category === 'nsfw' && '不適切なコンテンツ'}
                          {violation.category === 'before_after' && 'ビフォーアフター表現'}
                          {violation.category === 'misleading' && '誇大広告表現'}
                        </Typography>
                        <Chip
                          label={violation.severity === 'high' ? '高' : violation.severity === 'medium' ? '中' : '低'}
                          size="small"
                          sx={{
                            fontWeight: 700,
                            bgcolor:
                              violation.severity === 'high'
                                ? '#fee2e2'
                                : violation.severity === 'medium'
                                ? '#fef3c7'
                                : '#e0e7ff',
                            color:
                              violation.severity === 'high'
                                ? '#dc2626'
                                : violation.severity === 'medium'
                                ? '#d97706'
                                : '#4f46e5',
                          }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {violation.description}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Paper>
            )}

            {/* 改善提案（強化版） */}
            <EnhancedRecommendations
              recommendations={result.recommendations}
              imageImprovement={result.image_improvement}
              currentScore={result.overall_score}
            />

            {/* 詳細情報 */}
            <Paper elevation={2} sx={{ p: 4, borderRadius: 4, mb: 3 }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
                詳細情報
              </Typography>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
                  gap: 2.5,
                }}
              >
                {result.text_overlay_percentage !== undefined && (
                  <Box
                    sx={{
                      bgcolor: '#f8fafc',
                      p: 3,
                      borderRadius: 3,
                      textAlign: 'center',
                      border: '2px solid transparent',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        borderColor: '#10b981',
                        boxShadow: '0 8px 16px rgba(16, 185, 129, 0.15)',
                      },
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontWeight: 800,
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                        mb: 1,
                      }}
                    >
                      {result.text_overlay_percentage}%
                    </Typography>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      画像内テキスト量
                    </Typography>
                  </Box>
                )}
                <Box
                  sx={{
                    bgcolor: '#f8fafc',
                    p: 3,
                    borderRadius: 3,
                    textAlign: 'center',
                    border: '2px solid transparent',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      borderColor: '#10b981',
                      boxShadow: '0 8px 16px rgba(16, 185, 129, 0.15)',
                    },
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{
                      fontWeight: 800,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      mb: 1,
                    }}
                  >
                    {Math.round(result.confidence * 100)}%
                  </Typography>
                  <Typography variant="body2" fontWeight={600} color="text.secondary">
                    信頼度
                  </Typography>
                </Box>
                <Box
                  sx={{
                    bgcolor: '#f8fafc',
                    p: 3,
                    borderRadius: 3,
                    textAlign: 'center',
                    border: '2px solid transparent',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      borderColor: '#10b981',
                      boxShadow: '0 8px 16px rgba(16, 185, 129, 0.15)',
                    },
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{
                      fontWeight: 800,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      mb: 1,
                    }}
                  >
                    {result.nsfw_detected ? 'あり' : 'なし'}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} color="text.secondary">
                    NSFW検出
                  </Typography>
                </Box>
              </Box>
            </Paper>

            {/* 再チェックボタン */}
            <Paper elevation={2} sx={{ p: 4, borderRadius: 4 }}>
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={resetForm}
                startIcon={<RefreshIcon />}
                sx={{
                  py: 2,
                  fontSize: '1rem',
                  fontWeight: 600,
                  borderWidth: 2,
                  '&:hover': {
                    borderWidth: 2,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                修正内容を再チェック
              </Button>
            </Paper>
          </>
        )}
      </Box>
    </PublicLayout>
  );
};
