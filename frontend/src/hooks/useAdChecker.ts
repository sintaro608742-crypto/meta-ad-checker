// ============================================
// useAdChecker - 広告チェック用カスタムフック
// URL審査専用（シンプル版）
// ============================================

import { useState, useCallback } from 'react';
import type {
  AdCheckRequest,
  AdCheckResponse,
  AdFormData,
  CheckState,
} from '@/types';
import { AdCheckerService } from '@/services/AdCheckerService';
import { logger } from '@/lib/logger';

const service = new AdCheckerService();

export const useAdChecker = () => {
  // フォームデータ（URLのみ）
  const [formData, setFormData] = useState<AdFormData>({
    pageUrl: '',
  });

  // チェック状態
  const [checkState, setCheckState] = useState<CheckState>({
    isLoading: false,
    hasResult: false,
    error: null,
  });

  // チェック結果
  const [result, setResult] = useState<AdCheckResponse | null>(null);

  /**
   * フォームフィールド更新
   */
  const updateField = useCallback(
    (field: keyof AdFormData, value: string) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
      logger.debug('Form field updated', { field, hasValue: !!value });
    },
    []
  );

  /**
   * 広告チェック実行
   */
  const checkAdvertisement = useCallback(async () => {
    try {
      // バリデーション
      if (!formData.pageUrl) {
        const errorMessage = 'URLを入力してください';
        logger.warn('Validation failed', { reason: errorMessage });
        setCheckState((prev) => ({ ...prev, error: errorMessage }));
        return;
      }

      logger.debug('Starting advertisement check', {
        pageUrl: formData.pageUrl,
      });

      setCheckState({
        isLoading: true,
        hasResult: false,
        error: null,
      });

      // リクエスト作成
      const request: AdCheckRequest = {
        page_url: formData.pageUrl,
      };

      // API呼び出し
      const response = await service.checkAdvertisement(request);

      logger.info('Advertisement check completed', {
        status: response.status,
        score: response.overall_score,
        violationCount: response.violations.length,
      });

      setResult(response);
      setCheckState({
        isLoading: false,
        hasResult: true,
        error: null,
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Advertisement check failed', {
        error: error.message,
        stack: error.stack,
      });

      setCheckState({
        isLoading: false,
        hasResult: false,
        error: error.message,
      });
    }
  }, [formData]);

  /**
   * フォームをリセット（再チェック用）
   */
  const resetForm = useCallback(() => {
    logger.debug('Resetting form and results');

    setCheckState({
      isLoading: false,
      hasResult: false,
      error: null,
    });
    setResult(null);
  }, []);

  /**
   * すべてをクリア
   */
  const clearAll = useCallback(() => {
    logger.debug('Clearing all data');

    setFormData({
      pageUrl: '',
    });

    setCheckState({
      isLoading: false,
      hasResult: false,
      error: null,
    });
    setResult(null);
  }, []);

  /**
   * 入力があるかチェック
   */
  const hasInput = !!formData.pageUrl;

  return {
    // データ
    formData,
    checkState,
    result,
    hasInput,

    // アクション
    updateField,
    checkAdvertisement,
    resetForm,
    clearAll,
  };
};
