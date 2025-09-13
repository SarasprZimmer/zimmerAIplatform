'use server'

import { jwtVerify } from 'jose'

/**
 * Verify and decode a JWT token using the shared secret.
 *
 * @param token - JWT token string from client
 * @returns The decoded JWT payload if valid, otherwise null
 */
export async function verifyToken(token: string): Promise<Record<string, any> | null> {
  const secret = process.env.JWT_SECRET_KEY
  if (!secret) {
    console.error('JWT_SECRET_KEY is not set')
    return null
  }

  try {
    const key = new TextEncoder().encode(secret)
    const { payload } = await jwtVerify(token, key)
    return payload
  } catch (error) {
    console.error('Failed to verify token:', error)
    return null
  }
}

