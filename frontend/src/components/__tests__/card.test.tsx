import { render, screen } from '@testing-library/react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';

describe('Card Components', () => {
  it('renders Card with content', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
          <CardDescription>Test Description</CardDescription>
        </CardHeader>
        <CardContent>Test Content</CardContent>
      </Card>
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
        </CardHeader>
        <CardContent>Content</CardContent>
      </Card>
    );

    const card = container.firstChild;
    expect(card).toHaveClass('rounded-lg', 'border', 'bg-card');

    const header = screen.getByText('Title').closest('div');
    expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6');

    const content = screen.getByText('Content').closest('div');
    expect(content).toHaveClass('p-6', 'pt-0');
  });

  it('renders without optional props', () => {
    render(
      <Card>
        <CardContent>Content only</CardContent>
      </Card>
    );

    expect(screen.getByText('Content only')).toBeInTheDocument();
  });
});
