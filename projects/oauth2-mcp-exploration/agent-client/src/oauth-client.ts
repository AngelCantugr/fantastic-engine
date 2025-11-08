/**
 * OAuth 2.0 Client for AI Agent
 * Handles token acquisition and refresh using client_credentials grant
 */

import axios from 'axios';
import { AccessToken } from 'shared';

export class OAuthClient {
  private accessToken: string | null = null;
  private tokenExpiry: number | null = null;

  constructor(
    private authServerUrl: string,
    private clientId: string,
    private clientSecret: string,
    private scope: string[]
  ) {}

  /**
   * Get a valid access token (fetches new one if needed)
   */
  async getAccessToken(): Promise<string> {
    // Check if we have a valid token
    if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      console.log('[Agent-OAuth] Using cached access token');
      return this.accessToken;
    }

    // Fetch new token
    console.log('[Agent-OAuth] Fetching new access token...');
    await this.fetchAccessToken();

    if (!this.accessToken) {
      throw new Error('Failed to obtain access token');
    }

    return this.accessToken;
  }

  /**
   * Fetch access token using client_credentials grant
   */
  private async fetchAccessToken(): Promise<void> {
    try {
      const response = await axios.post<AccessToken>(
        `${this.authServerUrl}/oauth/token`,
        {
          grant_type: 'client_credentials',
          client_id: this.clientId,
          client_secret: this.clientSecret,
          scope: this.scope.join(' '),
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      this.accessToken = response.data.access_token;
      // Set expiry with 5 minute buffer
      this.tokenExpiry = Date.now() + (response.data.expires_in - 300) * 1000;

      console.log('[Agent-OAuth] ✓ Access token obtained successfully');
      console.log(`[Agent-OAuth]   Scopes: ${response.data.scope}`);
      console.log(`[Agent-OAuth]   Expires in: ${response.data.expires_in}s`);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('[Agent-OAuth] ✗ Failed to fetch token:', error.response?.data);
        throw new Error(`OAuth error: ${JSON.stringify(error.response?.data)}`);
      }
      throw error;
    }
  }

  /**
   * Make an authenticated request to a protected resource
   */
  async authenticatedRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: unknown
  ): Promise<T> {
    const token = await this.getAccessToken();

    try {
      const response = await axios({
        method,
        url,
        data,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          // Token might be invalid, clear cache and retry once
          console.log('[Agent-OAuth] Token invalid, clearing cache and retrying...');
          this.accessToken = null;
          this.tokenExpiry = null;

          const newToken = await this.getAccessToken();
          const retryResponse = await axios({
            method,
            url,
            data,
            headers: {
              Authorization: `Bearer ${newToken}`,
              'Content-Type': 'application/json',
            },
          });

          return retryResponse.data;
        }

        throw new Error(`API error: ${JSON.stringify(error.response?.data)}`);
      }
      throw error;
    }
  }
}
