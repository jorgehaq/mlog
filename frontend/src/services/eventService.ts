import { api } from './api'

export const sendEvent = async (event: any) => {
  const response = await api.post('/events', event)
  return response.data
}

