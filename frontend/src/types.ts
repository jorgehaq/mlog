import { z } from 'zod'

export const HealthSchema = z.object({
  status: z.string(),
  mongo: z.boolean().optional(),
})
export type Health = z.infer<typeof HealthSchema>

export const RootSchema = z.object({
  app: z.string(),
  message: z.string(),
})
export type RootInfo = z.infer<typeof RootSchema>

