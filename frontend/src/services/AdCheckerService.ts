// ============================================
// AdCheckerService - 広告審査API統合サービス
// URL審査専用（シンプル版）
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
   * URL審査を実行（実API統合）
   * エンドポイント: POST /api/check
   */
  async checkAdvertisement(request: AdCheckRequest): Promise<AdCheckResponse> {
    logger.debug('AdChecker: Starting URL check', {
      pageUrl: request.page_url,
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
}
