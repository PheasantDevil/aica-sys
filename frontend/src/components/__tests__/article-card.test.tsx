import { render, screen } from "@/test-utils/test-utils";
import { ArticleCard } from "@/components/content/article-card";

const mockArticle = {
  id: "1",
  title: "Test Article Title",
  description: "Test article description that is long enough to test truncation",
  content: "Test content",
  author: {
    name: "Test Author",
    avatar: "/test-avatar.jpg",
  },
  category: "tutorial",
  tags: ["TypeScript", "React", "Testing"],
  publishedAt: "2024-01-15T10:00:00Z",
  readTime: 5,
  views: 1000,
  likes: 50,
  isPremium: false,
  imageUrl: "/test-image.jpg",
};

describe("ArticleCard", () => {
  it("renders article information correctly", () => {
    render(<ArticleCard article={mockArticle} />);

    expect(screen.getByText("Test Article Title")).toBeInTheDocument();
    expect(
      screen.getByText("Test article description that is long enough to test truncation"),
    ).toBeInTheDocument();
    expect(screen.getByText("Test Author")).toBeInTheDocument();
    expect(screen.getByText("tutorial")).toBeInTheDocument();
    expect(screen.getByText("5分")).toBeInTheDocument();
    expect(screen.getByText("1,000")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();
  });

  it("renders premium badge when article is premium", () => {
    const premiumArticle = { ...mockArticle, isPremium: true };
    render(<ArticleCard article={premiumArticle} />);

    expect(screen.getByText("Premium")).toBeInTheDocument();
  });

  it("renders tags correctly", () => {
    render(<ArticleCard article={mockArticle} />);

    expect(screen.getByText("#TypeScript")).toBeInTheDocument();
    expect(screen.getByText("#React")).toBeInTheDocument();
    expect(screen.getByText("#Testing")).toBeInTheDocument();
  });

  it("has correct link to article page", () => {
    render(<ArticleCard article={mockArticle} />);

    const link = screen.getByRole("link", { name: "Test Article Title" });
    expect(link).toHaveAttribute("href", "/articles/1");
  });

  it("renders read button with correct link", () => {
    render(<ArticleCard article={mockArticle} />);

    const readButton = screen.getByRole("link", { name: "読む" });
    expect(readButton).toHaveAttribute("href", "/articles/1");
  });
});
