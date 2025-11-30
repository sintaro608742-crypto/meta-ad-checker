// ============================================
// ApiClient - HTTP通信の基盤クライアント
// ============================================

import axios, { type AxiosInstance, type AxiosError } from 'axios';
import { logger } from '@/lib/logger';
import type { ApiError } from '@/types';

/**
 * API通信用のaxiosインスタンス
 */
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    // 本番環境では本番APIを使用、それ以外は環境変数またはローカル
    const isProduction = window.location.hostname === 'meta-ad-checker.vercel.app';
    const apiUrl = isProduction
      ? 'https://meta-ad-checker.onrender.com'
      : (import.meta.env.VITE_API_URL || 'http://localhost:8432');

    this.client = axios.create({
      baseURL: apiUrl,
      timeout: 30000, // 30秒（CLAUDE.md準拠）
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // リクエストインターセプター
    this.client.interceptors.request.use(
      (config) => {
        logger.debug('API Request', {
          method: config.method,
          url: config.url,
          hasData: !!config.data,
        });
        return config;
      },
      (error) => {
        logger.error('API Request Error', { error: error.message });
        return Promise.reject(error);
      }
    );

    // レスポンスインターセプター
    this.client.interceptors.response.use(
      (response) => {
        logger.debug('API Response', {
          status: response.status,
          url: response.config.url,
        });
        return response;
      },
      (error: AxiosError<ApiError>) => {
        // エラーハンドリング
        if (error.response) {
          // サーバーエラー（4xx, 5xx）
          logger.error('API Response Error', {
            status: error.response.status,
            message: error.response.data?.message || error.message,
            url: error.config?.url,
          });

          // ユーザーフレンドリーなエラーメッセージに変換
          const errorMessage = this.getErrorMessage(error);
          throw new Error(errorMessage);
        } else if (error.request) {
          // ネットワークエラー（リクエストは送信されたが応答なし）
          logger.error('API Network Error', {
            message: 'サーバーに接続できません',
            url: error.config?.url,
          });
          throw new Error(
            'サーバーに接続できません。バックエンドが起動していることを確認してください。'
          );
        } else {
          // その他のエラー
          logger.error('API Unknown Error', { error: error.message });
          throw new Error('予期しないエラーが発生しました');
        }
      }
    );

    logger.info('ApiClient initialized', { baseURL: apiUrl });
  }

  /**
   * エラーレスポンスからユーザーフレンドリーなメッセージを生成
   */
  private getErrorMessage(error: AxiosError<ApiError>): string {
    const status = error.response?.status;
    const apiError = error.response?.data;

    // APIエラーレスポンスのメッセージを優先
    if (apiError?.message) {
      return apiError.message;
    }

    // HTTPステータスコードに基づくデフォルトメッセージ
    switch (status) {
      case 400:
        return 'リクエストの内容に誤りがあります';
      case 413:
        return 'ファイルサイズが大きすぎます（最大20MB）';
      case 415:
        return '対応していないファイル形式です（JPEG, PNG, WebPのみ対応）';
      case 429:
        return 'リクエストが多すぎます。しばらく待ってから再試行してください';
      case 500:
        return 'サーバーエラーが発生しました。時間をおいて再試行してください';
      case 503:
        return 'サービスが一時的に利用できません。時間をおいて再試行してください';
      default:
        return apiError?.error || 'エラーが発生しました';
    }
  }

  /**
   * GETリクエスト
   */
  async get<T>(url: string): Promise<T> {
    const response = await this.client.get<T>(url);
    return response.data;
  }

  /**
   * POSTリクエスト
   */
  async post<T, D = unknown>(url: string, data?: D): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }
}

// シングルトンインスタンス
export const apiClient = new ApiClient();
