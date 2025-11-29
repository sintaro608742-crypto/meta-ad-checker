import {
  Box,
  Paper,
  Typography,
  Link,
  List,
  ListItem,
  ListItemText,
  Button,
} from '@mui/material';
import { PublicLayout } from '../layouts/PublicLayout';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import type { StepItem, FaqItem } from '../types';

export const GuidePage = () => {
  const navigate = useNavigate();

  // 3ステップ
  const steps: StepItem[] = [
    {
      number: 1,
      title: 'テキストを入力',
      description: '広告の見出し、説明文、CTAを入力します（任意）',
    },
    {
      number: 2,
      title: '画像をアップロード',
      description: '広告画像をドラッグ&ドロップまたは選択します（任意）',
    },
    {
      number: 3,
      title: 'チェック実行',
      description: '30秒以内にAI審査結果と改善提案を取得できます',
    },
  ];

  // FAQ
  const faqs: FaqItem[] = [
    {
      question: 'テキストだけ、または画像だけでもチェックできますか?',
      answer:
        'はい、可能です。テキストまたは画像の少なくとも1つがあればチェックできます。両方入力すると、より精度の高い審査予測が得られます。',
    },
    {
      question: 'アップロードできる画像の形式とサイズは?',
      answer: 'JPEG、PNG、WebP形式に対応しており、最大20MBまでアップロード可能です。',
    },
    {
      question: 'チェック結果はどのくらい正確ですか?',
      answer:
        'AIベースの審査予測のため、80-90%程度の高精度ですが、100%の保証はできません。Metaの審査基準は頻繁に更新されるため、あくまで参考としてご利用ください。',
    },
    {
      question: 'アカウント登録は必要ですか?',
      answer: 'いいえ、現在はアカウント登録なしで全機能を無料でご利用いただけます。',
    },
    {
      question: 'チェック履歴は保存されますか?',
      answer:
        '現在のバージョンでは、チェック履歴は保存されません。将来的にアカウント機能と共に実装予定です。',
    },
    {
      question: '審査に落ちた広告を改善する方法は?',
      answer:
        'チェック結果に表示される「改善提案」セクションに、具体的な修正案と理由が記載されています。それらを参考に修正後、再度チェックすることをおすすめします。',
    },
  ];

  return (
    <PublicLayout maxWidth="md">
      <Box sx={{ py: 4 }}>
        {/* タイトル */}
        <Typography
          variant="h2"
          component="h1"
          sx={{
            fontSize: { xs: '2rem', md: '3rem' },
            fontWeight: 800,
            mb: 2,
            color: '#ffffff',
            textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
            letterSpacing: '-0.02em',
            textAlign: 'center',
            animation: 'fadeInDown 0.8s ease-out',
            '@keyframes fadeInDown': {
              from: { opacity: 0, transform: 'translateY(-20px)' },
              to: { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          使い方ガイド / FAQ
        </Typography>
        <Typography
          variant="body1"
          sx={{
            textAlign: 'center',
            fontSize: '1.125rem',
            color: '#ffffff',
            textShadow: '0 1px 5px rgba(0, 0, 0, 0.15)',
            mb: 6,
            animation: 'fadeInDown 0.8s ease-out 0.2s backwards',
          }}
        >
          メタ広告審査チェッカーの使い方を簡単にご紹介します
        </Typography>

        {/* メタ広告審査の基礎知識 */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            mb: 3,
            borderRadius: 4,
            transition: 'all 0.3s ease',
            animation: 'fadeInUp 0.6s ease-out 0.1s backwards',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
            '@keyframes fadeInUp': {
              from: { opacity: 0, transform: 'translateY(20px)' },
              to: { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          <Typography
            variant="h5"
            sx={{
              mb: 3,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              '&::before': {
                content: '""',
                width: '4px',
                height: '28px',
                background: 'linear-gradient(180deg, #10b981 0%, #059669 100%)',
                borderRadius: '2px',
              },
            }}
          >
            メタ広告審査の基礎知識
          </Typography>
          <Typography variant="body1" paragraph sx={{ color: 'text.secondary', lineHeight: 1.8 }}>
            メタ広告では、広告が掲載される前に自動審査と人間による審査が行われます。主に以下の5つのポイントがチェックされます。
          </Typography>
          <List>
            {[
              {
                title: '画像内テキスト量',
                desc: '20%以下が推奨（超過するとリーチが制限される可能性）',
              },
              {
                title: '禁止コンテンツ',
                desc: 'アルコール、タバコ、医薬品、武器等の制限対象コンテンツ',
              },
              {
                title: '過度な肌露出・性的表現',
                desc: '不適切な画像や表現の禁止',
              },
              {
                title: 'ビフォーアフター表現',
                desc: 'ダイエット、美容系広告での誇張表現',
              },
              {
                title: '誇大広告・誤解を招く表現',
                desc: '「最安値」「絶対」等の断定表現',
              },
            ].map((item, index) => (
              <ListItem
                key={index}
                sx={{
                  pl: 0,
                  mb: 1.5,
                  alignItems: 'flex-start',
                }}
              >
                <Box
                  sx={{
                    mr: 2,
                    mt: 0.5,
                    color: '#10b981',
                    fontWeight: 700,
                    fontSize: '1.125rem',
                  }}
                >
                  ✓
                </Box>
                <ListItemText
                  primary={<strong>{item.title}</strong>}
                  secondary={item.desc}
                  primaryTypographyProps={{ sx: { color: 'text.primary', fontWeight: 600 } }}
                  secondaryTypographyProps={{ sx: { color: 'text.secondary', lineHeight: 1.7 } }}
                />
              </ListItem>
            ))}
          </List>
          <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
            このアプリでは、これらの審査基準を総合的にチェックし、事前に問題を発見できます。
          </Typography>
        </Paper>

        {/* 使い方（3ステップ） */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            mb: 3,
            borderRadius: 4,
            transition: 'all 0.3s ease',
            animation: 'fadeInUp 0.6s ease-out 0.2s backwards',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
          }}
        >
          <Typography
            variant="h5"
            sx={{
              mb: 3,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              '&::before': {
                content: '""',
                width: '4px',
                height: '28px',
                background: 'linear-gradient(180deg, #10b981 0%, #059669 100%)',
                borderRadius: '2px',
              },
            }}
          >
            使い方（3ステップ）
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
              gap: 3,
              mt: 3,
            }}
          >
            {steps.map((step) => (
              <Box
                key={step.number}
                sx={{
                  background: 'linear-gradient(135deg, #f0fdfa 0%, #ecfdf5 100%)',
                  borderRadius: 3,
                  p: 3.5,
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  border: '2px solid transparent',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    borderColor: '#10b981',
                    boxShadow: '0 8px 16px rgba(16, 185, 129, 0.2)',
                  },
                }}
              >
                <Typography
                  variant="h2"
                  sx={{
                    fontSize: '3rem',
                    fontWeight: 800,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    mb: 1.5,
                  }}
                >
                  {step.number}
                </Typography>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    color: 'text.primary',
                    mb: 1.5,
                  }}
                >
                  {step.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'text.secondary',
                    lineHeight: 1.7,
                  }}
                >
                  {step.description}
                </Typography>
              </Box>
            ))}
          </Box>
          <Typography
            variant="body2"
            sx={{
              mt: 3,
              textAlign: 'center',
              color: 'text.secondary',
            }}
          >
            ※テキストまたは画像の少なくとも1つは必須です
          </Typography>
        </Paper>

        {/* よくある質問（FAQ） */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            mb: 3,
            borderRadius: 4,
            transition: 'all 0.3s ease',
            animation: 'fadeInUp 0.6s ease-out 0.3s backwards',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: 4,
            },
          }}
        >
          <Typography
            variant="h5"
            sx={{
              mb: 3,
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              '&::before': {
                content: '""',
                width: '4px',
                height: '28px',
                background: 'linear-gradient(180deg, #10b981 0%, #059669 100%)',
                borderRadius: '2px',
              },
            }}
          >
            よくある質問（FAQ）
          </Typography>
          {faqs.map((faq, index) => (
            <Box
              key={index}
              sx={{
                background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                borderRadius: 3,
                p: 3,
                mb: 2,
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                border: '2px solid transparent',
                '&:hover': {
                  borderColor: '#10b981',
                  boxShadow: '0 4px 12px rgba(16, 185, 129, 0.1)',
                  transform: 'translateX(4px)',
                },
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  mb: 1.5,
                }}
              >
                <Box
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 32,
                    height: 32,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    borderRadius: '50%',
                    fontWeight: 700,
                    fontSize: '1rem',
                    flexShrink: 0,
                  }}
                >
                  Q
                </Box>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 600,
                    color: 'text.primary',
                  }}
                >
                  {faq.question}
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
                  lineHeight: 1.8,
                  pl: 5,
                }}
              >
                {faq.answer}
              </Typography>
            </Box>
          ))}
        </Paper>

        {/* メタ広告ポリシーリンク */}
        <Paper
          elevation={2}
          sx={{
            p: 4,
            mb: 3,
            borderRadius: 4,
            animation: 'fadeInUp 0.6s ease-out 0.4s backwards',
          }}
        >
          <Box
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 3,
              p: 4,
              textAlign: 'center',
              color: 'white',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 1.5, position: 'relative', zIndex: 1 }}>
              さらに詳しく知りたい方へ
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, opacity: 0.95, position: 'relative', zIndex: 1 }}>
              Meta公式の広告ポリシーをご確認ください
            </Typography>
            <Link
              href="https://www.facebook.com/policies/ads/"
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                background: 'rgba(255, 255, 255, 0.95)',
                color: '#059669',
                px: 3,
                py: 1.5,
                borderRadius: 2,
                textDecoration: 'none',
                fontWeight: 600,
                transition: 'all 0.3s ease',
                position: 'relative',
                zIndex: 1,
                '&:hover': {
                  background: '#ffffff',
                  transform: 'scale(1.05)',
                  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
                },
              }}
            >
              Meta広告ポリシーを見る
              <OpenInNewIcon sx={{ fontSize: 18 }} />
            </Link>
          </Box>
        </Paper>

        {/* チェッカーに戻るボタン */}
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
            sx={{
              py: 1.75,
              px: 3.5,
              fontSize: '1rem',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 20px rgba(16, 185, 129, 0.4)',
              },
            }}
          >
            チェッカーに戻る
          </Button>
        </Box>
      </Box>
    </PublicLayout>
  );
};
