// ============================================
// useAdChecker - 広告チェック用カスタムフック
// ============================================

import { useState, useCallback } from 'react';
import type {
  AdCheckRequest,
  AdCheckResponse,
  AdFormData,
  CheckState,
  ImagePreview,
} from '@/types';
import { AdCheckerService } from '@/services/AdCheckerService';
import { logger } from '@/lib/logger';

const service = new AdCheckerService();

export const useAdChecker = () => {
  // フォームデータ
  const [formData, setFormData] = useState<AdFormData>({
    headline: '',
    description: '',
    cta: '',
    imageFile: null,
  });

  // 画像プレビュー
  const [imagePreview, setImagePreview] = useState<ImagePreview | null>(null);

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
    (field: keyof AdFormData, value: string | File | null) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
      logger.debug('Form field updated', { field, hasValue: !!value });
    },
    []
  );

  /**
   * 画像ファイルをアップロード
   */
  const handleImageUpload = useCallback(async (file: File) => {
    try {
      logger.debug('Image upload started', {
        name: file.name,
        size: file.size,
        type: file.type,
      });

      // バリデーション
      service.validateImageFile(file);

      // プレビューURL生成
      const previewUrl = URL.createObjectURL(file);

      setImagePreview({ file, previewUrl });
      setFormData((prev) => ({ ...prev, imageFile: file }));

      logger.info('Image uploaded successfully', { name: file.name });
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Image upload failed', {
        error: error.message,
        fileName: file.name,
      });

      setCheckState((prev) => ({
        ...prev,
        error: error.message,
      }));

      // エラーを上位に伝播
      throw error;
    }
  }, []);

  /**
   * 画像をクリア
   */
  const clearImage = useCallback(() => {
    if (imagePreview?.previewUrl) {
      URL.revokeObjectURL(imagePreview.previewUrl);
    }
    setImagePreview(null);
    setFormData((prev) => ({ ...prev, imageFile: null }));
    logger.debug('Image cleared');
  }, [imagePreview]);

  /**
   * 広告チェック実行
   */
  const checkAdvertisement = useCallback(async () => {
    try {
      // バリデーション
      if (!formData.headline && !formData.description && !formData.cta && !formData.imageFile) {
        const errorMessage = 'テキストまたは画像の少なくとも1つを入力してください';
        logger.warn('Validation failed', { reason: errorMessage });
        setCheckState((prev) => ({ ...prev, error: errorMessage }));
        return;
      }

      logger.debug('Starting advertisement check', {
        hasHeadline: !!formData.headline,
        hasDescription: !!formData.description,
        hasCta: !!formData.cta,
        hasImage: !!formData.imageFile,
      });

      setCheckState({
        isLoading: true,
        hasResult: false,
        error: null,
      });

      // リクエスト作成
      const request: AdCheckRequest = {
        headline: formData.headline || undefined,
        description: formData.description || undefined,
        cta: formData.cta || undefined,
      };

      // 画像がある場合はBase64変換
      if (formData.imageFile) {
        const base64 = await service.fileToBase64(formData.imageFile);
        request.image = base64;
        logger.debug('Image converted to base64', {
          originalSize: formData.imageFile.size,
        });
      }

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

    // 画像プレビューはクリアしない（再チェック時に同じ画像を使用可能にするため）
  }, []);

  /**
   * すべてをクリア
   */
  const clearAll = useCallback(() => {
    logger.debug('Clearing all data');

    setFormData({
      headline: '',
      description: '',
      cta: '',
      imageFile: null,
    });

    if (imagePreview?.previewUrl) {
      URL.revokeObjectURL(imagePreview.previewUrl);
    }
    setImagePreview(null);

    setCheckState({
      isLoading: false,
      hasResult: false,
      error: null,
    });
    setResult(null);
  }, [imagePreview]);

  /**
   * 入力があるかチェック
   */
  const hasInput = !!(
    formData.headline ||
    formData.description ||
    formData.cta ||
    formData.imageFile
  );

  return {
    // データ
    formData,
    imagePreview,
    checkState,
    result,
    hasInput,

    // アクション
    updateField,
    handleImageUpload,
    clearImage,
    checkAdvertisement,
    resetForm,
    clearAll,
  };
};
