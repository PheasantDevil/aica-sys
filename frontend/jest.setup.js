import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    }
  },
}))

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  usePathname() {
    return '/'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock NextAuth
jest.mock('next-auth/react', () => ({
  useSession: () => ({
    data: null,
    status: 'unauthenticated',
  }),
  signIn: jest.fn(),
  signOut: jest.fn(),
}))

// Mock Stripe
jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn(() => Promise.resolve({
    redirectToCheckout: jest.fn(),
  })),
}))

// Mock environment variables
process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = 'pk_test_mock'
process.env.NEXTAUTH_URL = 'http://localhost:3000'
process.env.NEXTAUTH_SECRET = 'mock-secret'

// Mock Next.js Response
global.Response = class Response {
  constructor(body, init) {
    this.body = body
    this.status = init?.status || 200
    this.headers = init?.headers || {}
  }
  
  async json() {
    return JSON.parse(this.body)
  }
}

// Mock Next.js Request
global.Request = class Request {
  constructor(url, init) {
    this.url = url
    this.method = init?.method || 'GET'
    this.headers = init?.headers || {}
  }
}
