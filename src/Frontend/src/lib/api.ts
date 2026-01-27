import { Ticket, TicketCategory, TicketStatus, User } from '@/types';

// PUNTO CHIAVE: Punta al tuo server Flask locale
const API_BASE_URL = 'http://localhost:5000/api';

// Helper per ottenere headers
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('cityfix_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

// Helper per gestire errori API
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    let errorMessage = `HTTP ${response.status}`;
    try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.message || errorMessage;
    } catch (e) {
        // Non è JSON, usa il testo raw
        errorMessage = errorText || errorMessage;
    }
    
    if (response.status === 401) {
      localStorage.removeItem('cityfix_token');
      localStorage.removeItem('cityfix_user');
      // Opzionale: window.location.href = '/login';
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

// ============ AUTH SERVICE ============

export const authApi = {
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },

  // QUESTA è la funzione che viene chiamata dalla pagina di registrazione
  register: async (data: { name: string; email: string; password: string; municipalityId: string }): Promise<{ message: string, id: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // Flask si aspetta: name, email, password, municipalityId
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  logout: async (): Promise<void> => {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
  },

  getProfile: async (): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};

// ============ TICKET SERVICE ============

export interface CreateTicketData {
  title: string;
  description: string;
  category: TicketCategory;
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  photos?: File[];
}

export interface UpdateTicketData {
  status?: TicketStatus;
  assignedOperatorId?: string;
  feedback?: {
    rating: number;
    comment?: string;
  };
}

export interface TicketFilters {
  status?: TicketStatus;
  category?: TicketCategory;
  municipalityId?: string;
  assignedOperatorId?: string;
  citizenId?: string;
}

export const ticketApi = {
  getAll: async (filters?: TicketFilters): Promise<Ticket[]> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    const response = await fetch(`${API_BASE_URL}/tickets?${params}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  getById: async (id: string): Promise<Ticket> => {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  create: async (data: CreateTicketData): Promise<Ticket> => {
    // 1. Recupera i dati dell'utente per associarli al ticket
    const userStr = localStorage.getItem('cityfix_user');
    const user = userStr ? JSON.parse(userStr) : null;

    // 2. Prepara il payload JSON
    const payload = {
        title: data.title,
        description: data.description,
        category: data.category,
        location: data.location,
        userId: user ? user.id : 'anonymous',
        municipalityId: user ? user.municipalityId : '1'
        // Ignoriamo le foto per ora per risolvere l'errore 415
    };

    // 3. Invia come JSON
    const response = await fetch(`${API_BASE_URL}/tickets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', // <--- QUESTO È FONDAMENTALE PER EVITARE 415
        ...(localStorage.getItem('cityfix_token') && { Authorization: `Bearer ${localStorage.getItem('cityfix_token')}` }),
      },
      body: JSON.stringify(payload),
    });

    return handleResponse(response);
  },

  update: async (id: string, data: UpdateTicketData): Promise<Ticket> => {
    const response = await fetch(`${API_BASE_URL}/tickets/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  assign: async (ticketId: string, operatorId: string): Promise<Ticket> => {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/assign`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ operatorId }),
    });
    return handleResponse(response);
  },

  complete: async (ticketId: string): Promise<Ticket> => {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/complete`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  addFeedback: async (ticketId: string, rating: number, comment?: string): Promise<Ticket> => {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/feedback`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ rating, comment }),
    });
    return handleResponse(response);
  },

  addComment: async (ticketId: string, text: string, authorName: string) => {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ text, authorName }),
    });
    return handleResponse(response);
  }
};

// ============ USER SERVICE (per Manager) ============

export const userApi = {
  getOperators: async (municipalityId?: string): Promise<User[]> => {
    const params = municipalityId ? `?municipalityId=${municipalityId}` : '';
    const response = await fetch(`${API_BASE_URL}/users/operators${params}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  createOperator: async (data: { name: string; email: string; category: TicketCategory }): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/users/operators`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// ============ STATS SERVICE (per Dashboard) ============

export interface DashboardStats {
  total: number;
  received: number;
  resolved: number;
  totalTickets: number;
  ticketsByStatus: Record<TicketStatus, number>;
  ticketsByCategory: Record<TicketCategory, number>;
  averageResolutionTime: number; // in ore
  ticketsThisMonth: number;
  resolvedThisMonth: number;
}

export const statsApi = {
  getDashboardStats: async (municipalityId?: string): Promise<DashboardStats> => {
    const params = municipalityId ? `?municipalityId=${municipalityId}` : '';
    const response = await fetch(`${API_BASE_URL}/stats/dashboard${params}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  getConsortiumStats: async (): Promise<{ municipalities: Array<{ id: string; name: string; stats: DashboardStats }> }> => {
    const response = await fetch(`${API_BASE_URL}/stats/consortium`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};