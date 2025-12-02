// ============================================
// AdCheckerService - 広告審査API統合サービス
// モックから実API統合に切り替え完了
// ============================================

import type {
  AdCheckRequest,
  AdCheckResponse,
  HealthCheckResponse,
} from '@/types';
import { apiClient } from './ApiClient';
import { logger } from '@/lib/logger';

export class AdCheckerService {
  /**
   * 広告チェックを実行（実API統合）
   * エンドポイント: POST /api/check
   */
  async checkAdvertisement(request: AdCheckRequest): Promise<AdCheckResponse> {
    logger.debug('AdChecker: Starting ad check', {
      hasHeadline: !!request.headline,
      hasDescription: !!request.description,
      hasCta: !!request.cta,
      hasImage: !!request.image,
      hasPageUrl: !!request.page_url,
    });

    try {
      const response = await apiClient.post<AdCheckResponse, AdCheckRequest>(
        '/api/check',
        request
      );

      logger.info('AdChecker: Check completed successfully', {
        status: response.status,
        score: response.overall_score,
        violationCount: response.violations.length,
      });

      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('AdChecker: Check failed', {
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * ヘルスチェック
   * エンドポイント: GET /api/health
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    logger.debug('AdChecker: Health check');

    try {
      const response = await apiClient.get<HealthCheckResponse>('/api/health');

      logger.info('AdChecker: Health check successful', {
        status: response.status,
      });

      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('AdChecker: Health check failed', {
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * ファイルをBase64文字列に変換
   * @param file - 変換するファイル
   * @returns Base64エンコードされた文字列
   */
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // "data:image/jpeg;base64," のプレフィックスを除去
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = () => {
        reject(new Error('ファイル読み込みに失敗しました'));
      };
      reader.readAsDataURL(file);
    });
  }

  /**
   * 画像ファイルのバリデーション
   * @param file - バリデーションするファイル
   * @throws バリデーションエラー
   */
  validateImageFile(file: File): void {
    const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB
    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];

    if (file.size > MAX_FILE_SIZE) {
      throw new Error('ファイルサイズは20MB以下にしてください');
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
      throw new Error('対応形式: JPEG, PNG, WebP, PDFのみアップロード可能です');
    }

    logger.debug('Image file validated', {
      name: file.name,
      size: file.size,
      type: file.type,
    });
  }
}
