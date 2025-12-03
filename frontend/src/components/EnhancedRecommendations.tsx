import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Collapse,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckIcon from '@mui/icons-material/Check';
import ErrorIcon from '@mui/icons-material/Error';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ImageIcon from '@mui/icons-material/Image';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import type { Recommendation, ImageImprovement, RecommendationPriority } from '../types';

interface EnhancedRecommendationsProps {
  recommendations: Recommendation[];
  imageImprovement?: ImageImprovement | null;
  currentScore: number;
}

// コピー状態管理用
const useCopyState = () => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // フォールバック
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  return { copiedId, copyToClipboard };
};

// 優先度別に改善提案をグループ化
const groupByPriority = (recommendations: Recommendation[]) => {
  const groups: Record<RecommendationPriority, Recommendation[]> = {
    must: [],
    recommended: [],
    optional: [],
  };

  recommendations.forEach((rec) => {
    if (groups[rec.priority]) {
      groups[rec.priority].push(rec);
    } else {
      groups.recommended.push(rec);
    }
  });

  return groups;
};

// 優先度設定
const priorityConfig = {
  must: {
    label: '必須の改善（これを直さないと審査落ち）',
    icon: <ErrorIcon />,
    color: '#dc2626',
    bgGradient: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
    borderColor: '#ef4444',
    badgeColor: '#fee2e2',
    badgeTextColor: '#dc2626',
  },
  recommended: {
    label: '推奨の改善（直すとスコアアップ）',
    icon: <TipsAndUpdatesIcon />,
    color: '#d97706',
    bgGradient: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
    borderColor: '#f59e0b',
    badgeColor: '#fef3c7',
    badgeTextColor: '#d97706',
  },
  optional: {
    label: '任意の改善（さらに良くしたい場合）',
    icon: <InfoOutlinedIcon />,
    color: '#0284c7',
    bgGradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
    borderColor: '#06b6d4',
    badgeColor: '#e0f2fe',
    badgeTextColor: '#0284c7',
  },
};

// 個別の改善提案アイテム
const RecommendationItem = ({
  rec,
  index,
  priority,
  copiedId,
  onCopy,
}: {
  rec: Recommendation;
  index: number;
  priority: RecommendationPriority;
  copiedId: string | null;
  onCopy: (text: string, id: string) => void;
}) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const config = priorityConfig[priority];

  const getTargetLabel = () => {
    if (rec.target === 'image') return '画像';
    switch (rec.target_field) {
      case 'headline': return '見出し';
      case 'description': return '説明文';
      case 'cta': return 'CTA';
      default: return 'テキスト';
    }
  };

  const getActionLabel = () => {
    switch (rec.action_type) {
      case 'replace': return '変更';
      case 'remove': return '削除';
      case 'reduce': return '削減';
      case 'rephrase': return '言い換え';
      case 'relocate': return '移動';
      default: return '改善';
    }
  };

  return (
    <Box
      sx={{
        background: config.bgGradient,
        borderLeft: `5px solid ${config.borderColor}`,
        borderRadius: 2,
        p: 2.5,
        mb: 2,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateX(4px)',
          boxShadow: `0 4px 12px ${config.borderColor}25`,
        },
      }}
    >
      {/* ヘッダー */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a', flex: 1, minWidth: 200 }}>
          {index + 1}. {rec.title}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={getTargetLabel()}
            size="small"
            sx={{ fontSize: '0.7rem', fontWeight: 700, bgcolor: '#f1f5f9', color: '#475569' }}
          />
          <Chip
            label={getActionLabel()}
            size="small"
            sx={{ fontSize: '0.7rem', fontWeight: 700, bgcolor: '#dbeafe', color: '#1d4ed8' }}
          />
          <Chip
            label={`+${rec.estimated_score_impact}点`}
            size="small"
            sx={{
              fontSize: '0.7rem',
              fontWeight: 800,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
            }}
          />
        </Box>
      </Box>

      {/* 現在の問題 */}
      <Box sx={{ mb: 2 }}>
        <Typography sx={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.08em', mb: 0.75 }}>
          現在の問題
        </Typography>
        <Box
          sx={{
            bgcolor: 'white',
            p: 1.5,
            borderRadius: 1,
            fontSize: '0.9rem',
            color: '#475569',
            border: '1px solid rgba(0,0,0,0.06)',
            position: 'relative',
            pl: 3,
            '&::before': {
              content: '"✗"',
              position: 'absolute',
              left: 12,
              color: '#ef4444',
              fontWeight: 'bold',
            },
          }}
        >
          {rec.before}
        </Box>
      </Box>

      {/* 修正候補 */}
      {rec.suggestions && rec.suggestions.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography sx={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.08em', mb: 0.75 }}>
            修正候補（クリックで選択）
          </Typography>
          <Stack spacing={1}>
            {rec.suggestions.map((suggestion, sIndex) => {
              const copyId = `${priority}-${index}-${sIndex}`;
              const isCopied = copiedId === copyId;
              const isSelected = selectedIndex === sIndex;

              return (
                <Box
                  key={sIndex}
                  onClick={() => setSelectedIndex(sIndex)}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    bgcolor: 'white',
                    p: 1.5,
                    borderRadius: 1,
                    border: isSelected ? '2px solid #10b981' : '2px solid #e2e8f0',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#10b981',
                      bgcolor: '#f0fdf4',
                    },
                  }}
                >
                  {/* ラジオボタン風 */}
                  <Box
                    sx={{
                      width: 18,
                      height: 18,
                      borderRadius: '50%',
                      border: isSelected ? '2px solid #10b981' : '2px solid #cbd5e1',
                      bgcolor: isSelected ? '#10b981' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    {isSelected && <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'white' }} />}
                  </Box>

                  <Typography sx={{ flex: 1, fontSize: '0.9rem', color: '#0f172a' }}>
                    {suggestion}
                  </Typography>

                  <Tooltip title={isCopied ? 'コピー完了!' : 'クリップボードにコピー'}>
                    <Button
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onCopy(suggestion, copyId);
                      }}
                      sx={{
                        minWidth: 'auto',
                        px: 1.5,
                        py: 0.5,
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        bgcolor: isCopied ? '#10b981' : '#f1f5f9',
                        color: isCopied ? 'white' : '#475569',
                        '&:hover': {
                          bgcolor: isCopied ? '#10b981' : '#10b981',
                          color: 'white',
                        },
                      }}
                      startIcon={isCopied ? <CheckIcon sx={{ fontSize: 14 }} /> : <ContentCopyIcon sx={{ fontSize: 14 }} />}
                    >
                      {isCopied ? '完了' : 'コピー'}
                    </Button>
                  </Tooltip>
                </Box>
              );
            })}
          </Stack>
        </Box>
      )}

      {/* 理由 */}
      <Box
        sx={{
          fontSize: '0.85rem',
          color: '#64748b',
          p: 1.5,
          bgcolor: 'rgba(255,255,255,0.6)',
          borderRadius: 1,
          lineHeight: 1.6,
        }}
      >
        <strong style={{ color: '#475569' }}>理由:</strong> {rec.reason}
      </Box>
    </Box>
  );
};

// 画像改善セクション
const ImageImprovementSection = ({ imageImprovement }: { imageImprovement: ImageImprovement }) => {
  const [expanded, setExpanded] = useState(true);
  const textOverlay = imageImprovement.text_overlay;

  // 画像がない場合（textOverlayがnull/undefinedまたはcurrent_percentageが0以下で内容がない）は非表示
  if (!textOverlay && imageImprovement.content_issues.length === 0) {
    return null;
  }

  // current_percentageが0%で、削除提案もない場合は非表示（画像がない可能性が高い）
  if (textOverlay && textOverlay.current_percentage === 0 &&
      (!textOverlay.removal_suggestions || textOverlay.removal_suggestions.length === 0) &&
      imageImprovement.content_issues.length === 0) {
    return null;
  }

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 4, mb: 3 }}>
      <Box
        sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
        onClick={() => setExpanded(!expanded)}
      >
        <Typography variant="h5" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
          <ImageIcon sx={{ color: '#7c3aed' }} />
          画像の改善
        </Typography>
        <IconButton size="small">
          {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      <Collapse in={expanded}>
        <Box
          sx={{
            mt: 3,
            background: 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)',
            border: '2px solid #c084fc',
            borderRadius: 3,
            p: 3,
          }}
        >
          {textOverlay && (
            <>
              <Typography sx={{ fontWeight: 700, fontSize: '1.1rem', color: '#7c3aed', display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                <TextFieldsIcon />
                画像内テキストの削減が必要
              </Typography>

              <Box sx={{ bgcolor: 'white', borderRadius: 2, p: 2.5, mb: 2.5 }}>
                {/* メーター */}
                <Box sx={{ mb: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography sx={{ fontSize: '0.85rem', fontWeight: 600, color: '#475569' }}>
                      テキスト占有率
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, fontSize: '0.85rem' }}>
                      <span style={{ color: '#ef4444', fontWeight: 700 }}>現在 {textOverlay.current_percentage}%</span>
                      <span style={{ color: '#94a3b8' }}>→</span>
                      <span style={{ color: '#10b981', fontWeight: 700 }}>目標 {textOverlay.target_percentage}%以下</span>
                    </Box>
                  </Box>
                  <Box sx={{ position: 'relative' }}>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(textOverlay.current_percentage, 100)}
                      sx={{
                        height: 12,
                        borderRadius: 6,
                        bgcolor: '#f1f5f9',
                        '& .MuiLinearProgress-bar': {
                          background: textOverlay.current_percentage <= 15
                            ? '#10b981'
                            : textOverlay.current_percentage <= 20
                              ? '#f59e0b'
                              : '#ef4444',
                          borderRadius: 6,
                        },
                      }}
                    />
                    {/* 目標ライン */}
                    <Box
                      sx={{
                        position: 'absolute',
                        left: `${textOverlay.target_percentage}%`,
                        top: -4,
                        bottom: -4,
                        width: 3,
                        bgcolor: '#10b981',
                        borderRadius: 1,
                        '&::after': {
                          content: '"目標"',
                          position: 'absolute',
                          top: -18,
                          left: '50%',
                          transform: 'translateX(-50%)',
                          fontSize: '0.65rem',
                          color: '#10b981',
                          fontWeight: 600,
                          whiteSpace: 'nowrap',
                        },
                      }}
                    />
                  </Box>
                </Box>

                {/* 問題箇所 */}
                {textOverlay.problematic_areas.length > 0 && (
                  <Box sx={{ mb: 2.5 }}>
                    <Typography sx={{ fontSize: '0.85rem', fontWeight: 700, color: '#dc2626', mb: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <ErrorIcon sx={{ fontSize: 18 }} />
                      削減が必要な箇所
                    </Typography>
                    <Stack spacing={1}>
                      {textOverlay.problematic_areas.map((area, idx) => (
                        <Box
                          key={idx}
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            p: 1.25,
                            bgcolor: '#fef2f2',
                            borderRadius: 1,
                            fontSize: '0.85rem',
                            color: '#991b1b',
                          }}
                        >
                          <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#ef4444', flexShrink: 0 }} />
                          {area}
                        </Box>
                      ))}
                    </Stack>
                  </Box>
                )}

                {/* 改善アドバイス */}
                {textOverlay.removal_suggestions.length > 0 && (
                  <Box sx={{ bgcolor: '#f0fdf4', borderRadius: 1.5, p: 2 }}>
                    <Typography sx={{ fontSize: '0.85rem', fontWeight: 700, color: '#16a34a', mb: 1.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <TipsAndUpdatesIcon sx={{ fontSize: 18 }} />
                      具体的な改善方法
                    </Typography>
                    <Stack spacing={1}>
                      {textOverlay.removal_suggestions.map((suggestion, idx) => (
                        <Box
                          key={idx}
                          sx={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: 1,
                            fontSize: '0.85rem',
                            color: '#166534',
                            lineHeight: 1.5,
                          }}
                        >
                          <CheckIcon sx={{ fontSize: 16, color: '#16a34a', mt: 0.25, flexShrink: 0 }} />
                          {suggestion}
                        </Box>
                      ))}
                    </Stack>
                  </Box>
                )}
              </Box>

              {/* ツール提案 */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  p: 2,
                  background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
                  borderRadius: 1.5,
                  border: '1px solid #93c5fd',
                }}
              >
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    bgcolor: 'white',
                    borderRadius: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                  }}
                >
                  <ImageIcon sx={{ fontSize: 28, color: '#3b82f6' }} />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography sx={{ fontWeight: 700, fontSize: '0.95rem', color: '#1e40af', mb: 0.25 }}>
                    Canvaで編集する
                  </Typography>
                  <Typography sx={{ fontSize: '0.8rem', color: '#64748b' }}>
                    無料で使える画像編集ツール。テキスト削除が簡単にできます
                  </Typography>
                </Box>
                <Button
                  href="https://www.canva.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  variant="contained"
                  endIcon={<OpenInNewIcon sx={{ fontSize: 16 }} />}
                  sx={{
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    fontWeight: 600,
                    fontSize: '0.85rem',
                    px: 2.5,
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
                    },
                  }}
                >
                  開く
                </Button>
              </Box>
            </>
          )}

          {/* コンテンツ問題 */}
          {imageImprovement.content_issues.length > 0 && (
            <Box sx={{ mt: textOverlay ? 3 : 0 }}>
              <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: '#7c3aed', mb: 2 }}>
                コンテンツの問題
              </Typography>
              <Stack spacing={2}>
                {imageImprovement.content_issues.map((issue, idx) => (
                  <Box key={idx} sx={{ bgcolor: 'white', borderRadius: 2, p: 2 }}>
                    <Typography sx={{ fontWeight: 700, color: '#dc2626', mb: 1 }}>
                      {issue.issue}
                    </Typography>
                    <Typography sx={{ fontSize: '0.85rem', color: '#64748b', mb: 1 }}>
                      場所: {issue.location}
                    </Typography>
                    {issue.alternatives.length > 0 && (
                      <Box>
                        <Typography sx={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', mb: 0.5 }}>
                          代替案:
                        </Typography>
                        {issue.alternatives.map((alt, aIdx) => (
                          <Typography key={aIdx} sx={{ fontSize: '0.85rem', color: '#166534', pl: 2 }}>
                            • {alt}
                          </Typography>
                        ))}
                      </Box>
                    )}
                  </Box>
                ))}
              </Stack>
            </Box>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

// メインコンポーネント
export const EnhancedRecommendations = ({
  recommendations,
  imageImprovement,
  currentScore,
}: EnhancedRecommendationsProps) => {
  const { copiedId, copyToClipboard } = useCopyState();
  const grouped = groupByPriority(recommendations);

  // 総スコアインパクトを計算
  const totalImpact = recommendations.reduce((sum, rec) => sum + rec.estimated_score_impact, 0);
  const predictedScore = Math.min(100, currentScore + totalImpact);

  // 改善提案がない場合
  if (recommendations.length === 0 && !imageImprovement) {
    return null;
  }

  return (
    <>
      {/* テキスト改善セクション */}
      {recommendations.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 4, mb: 3 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            <EditNoteIcon sx={{ color: '#10b981' }} />
            改善提案
          </Typography>

          {/* 優先度別セクション */}
          {(['must', 'recommended', 'optional'] as const).map((priority) => {
            const items = grouped[priority];
            if (items.length === 0) return null;

            const config = priorityConfig[priority];

            return (
              <Box key={priority} sx={{ mb: 3 }}>
                {/* セクションヘッダー */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.25,
                    mb: 2,
                    pb: 1.5,
                    borderBottom: '2px solid #f1f5f9',
                  }}
                >
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: config.badgeColor,
                      color: config.color,
                    }}
                  >
                    {config.icon}
                  </Box>
                  <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: config.color, flex: 1 }}>
                    {config.label}
                  </Typography>
                  <Chip
                    label={`${items.length}件`}
                    size="small"
                    sx={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      bgcolor: config.badgeColor,
                      color: config.badgeTextColor,
                    }}
                  />
                </Box>

                {/* アイテムリスト */}
                {items.map((rec, idx) => (
                  <RecommendationItem
                    key={`${priority}-${idx}`}
                    rec={rec}
                    index={idx}
                    priority={priority}
                    copiedId={copiedId}
                    onCopy={copyToClipboard}
                  />
                ))}
              </Box>
            );
          })}
        </Paper>
      )}

      {/* 画像改善セクション */}
      {imageImprovement && <ImageImprovementSection imageImprovement={imageImprovement} />}

      {/* 予想スコア改善サマリー */}
      {totalImpact > 0 && (
        <Box
          sx={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            borderRadius: 3,
            p: 3,
            color: 'white',
            textAlign: 'center',
            mb: 3,
          }}
        >
          <Typography sx={{ fontSize: '1rem', fontWeight: 600, mb: 0.5, opacity: 0.9 }}>
            すべての改善を実施した場合
          </Typography>
          <Typography sx={{ fontSize: '3rem', fontWeight: 800, mb: 0.5 }}>
            +{totalImpact}点
          </Typography>
          <Typography sx={{ fontSize: '0.85rem', opacity: 0.8 }}>
            現在 {currentScore}点 → 予想 {predictedScore}点
            {predictedScore >= 70 && ' (承認の可能性が高い)'}
          </Typography>
        </Box>
      )}
    </>
  );
};

export default EnhancedRecommendations;
