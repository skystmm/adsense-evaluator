/**
 * 认证工具函数
 */

/**
 * 获取存储的访问 Token
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * 获取存储的用户 ID
 */
export function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_id');
}

/**
 * 获取存储的用户邮箱
 */
export function getUserEmail(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('user_email');
}

/**
 * 检查用户是否已登录
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

/**
 * 登出用户
 */
export function logout(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_email');
}

/**
 * 获取认证请求头
 */
export function getAuthHeaders(): HeadersInit {
  const token = getAccessToken();
  if (token) {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }
  return {
    'Content-Type': 'application/json',
  };
}

/**
 * 检查 Token 是否过期（简单实现）
 * 可以通过解码 JWT 来检查实际过期时间
 */
export function isTokenExpired(): boolean {
  const token = getAccessToken();
  if (!token) return true;

  try {
    // 解码 JWT payload
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    
    // 检查 exp 字段
    if (payload.exp) {
      const now = Math.floor(Date.now() / 1000);
      return payload.exp < now;
    }
    
    return false;
  } catch {
    return true;
  }
}
