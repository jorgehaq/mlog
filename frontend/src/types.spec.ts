import { describe, it, expect } from 'vitest'
import { HealthSchema, RootSchema } from './types'

describe('Zod schemas', () => {
  it('parses valid health', () => {
    const v = HealthSchema.parse({ status: 'ok', mongo: true })
    expect(v.status).toBe('ok')
  })
  it('parses valid root', () => {
    const v = RootSchema.parse({ app: 'mlog', message: 'hi' })
    expect(v.app).toBe('mlog')
  })
  it('rejects invalid root', () => {
    expect(() => RootSchema.parse({})).toThrow()
  })
})

