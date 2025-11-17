import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useArticles } from "@/hooks/use-articles";
import { apiClient } from "@/lib/api-client";

// Mock the API client
jest.mock("@/lib/api-client");
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

// Mock NextAuth
jest.mock("next-auth/react", () => ({
  useSession: jest.fn(() => ({
    data: { user: { id: "1" } },
    status: "authenticated",
  })),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("useArticles", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should fetch articles successfully", async () => {
    const mockArticles = [
      {
        id: "1",
        title: "Test Article",
        description: "Test description",
        content: "Test content",
        author: { name: "Test Author" },
        category: "tutorial",
        tags: ["TypeScript"],
        publishedAt: "2024-01-15T10:00:00Z",
        readTime: 5,
        views: 100,
        likes: 10,
        isPremium: false,
      },
    ];

    mockedApiClient.getArticles.mockResolvedValue({
      data: { articles: mockArticles },
    });

    const { result } = renderHook(
      () => useArticles({ category: "all", sortBy: "newest", search: "" }),
      { wrapper: createWrapper() },
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toEqual(mockArticles);
    expect(mockedApiClient.getArticles).toHaveBeenCalledWith({
      category: undefined,
      sortBy: "newest",
      search: undefined,
    });
  });

  it("should handle API errors", async () => {
    mockedApiClient.getArticles.mockResolvedValue({
      error: "API Error",
    });

    const { result } = renderHook(
      () => useArticles({ category: "all", sortBy: "newest", search: "" }),
      { wrapper: createWrapper() },
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });

  it("should pass correct filters to API", async () => {
    mockedApiClient.getArticles.mockResolvedValue({
      data: { articles: [] },
    });

    const filters = {
      category: "tutorial",
      sortBy: "popular",
      search: "TypeScript",
    };

    renderHook(() => useArticles(filters), { wrapper: createWrapper() });

    await waitFor(() => {
      expect(mockedApiClient.getArticles).toHaveBeenCalledWith({
        category: "tutorial",
        sortBy: "popular",
        search: "TypeScript",
      });
    });
  });
});
