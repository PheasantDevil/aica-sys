"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { AccessibilityUtils } from "@/lib/accessibility";
import { useTranslations } from "next-intl";
import { AccessibleButton } from "@/components/ui/accessible-button";
import { AccessibleTextarea } from "@/components/ui/accessible-form";

interface Comment {
  id: string;
  content: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
    role?: string;
  };
  createdAt: string;
  updatedAt?: string;
  likes: number;
  dislikes: number;
  replies: Comment[];
  isLiked?: boolean;
  isDisliked?: boolean;
  isEdited?: boolean;
  isDeleted?: boolean;
}

interface CommentSystemProps {
  articleId: string;
  comments: Comment[];
  onCommentAdd?: (
    comment: Omit<Comment, "id" | "createdAt" | "likes" | "dislikes" | "replies">,
  ) => void;
  onCommentUpdate?: (commentId: string, content: string) => void;
  onCommentDelete?: (commentId: string) => void;
  onCommentLike?: (commentId: string) => void;
  onCommentDislike?: (commentId: string) => void;
  onReplyAdd?: (
    commentId: string,
    reply: Omit<Comment, "id" | "createdAt" | "likes" | "dislikes" | "replies">,
  ) => void;
  className?: string;
  maxDepth?: number;
  showReplies?: boolean;
  allowReplies?: boolean;
  allowEditing?: boolean;
  allowDeleting?: boolean;
  requireAuth?: boolean;
}

export function CommentSystem({
  articleId,
  comments,
  onCommentAdd,
  onCommentUpdate,
  onCommentDelete,
  onCommentLike,
  onCommentDislike,
  onReplyAdd,
  className,
  maxDepth = 3,
  showReplies = true,
  allowReplies = true,
  allowEditing = true,
  allowDeleting = true,
  requireAuth = true,
}: CommentSystemProps) {
  const t = useTranslations("common");
  const [newComment, setNewComment] = useState("");
  const [editingComment, setEditingComment] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState("");
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sortBy, setSortBy] = useState<"newest" | "oldest" | "popular">("newest");

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const replyTextareaRef = useRef<HTMLTextAreaElement>(null);

  // Sort comments
  const sortedComments = React.useMemo(() => {
    const sorted = [...comments].sort((a, b) => {
      switch (sortBy) {
        case "newest":
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case "oldest":
          return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
        case "popular":
          return b.likes - b.dislikes - (a.likes - a.dislikes);
        default:
          return 0;
      }
    });

    return sorted;
  }, [comments, sortBy]);

  // Handle comment submission
  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onCommentAdd?.({
        content: newComment.trim(),
        author: {
          id: "current-user", // This would come from auth context
          name: "Current User",
          avatar: "/avatars/default.jpg",
        },
      });
      setNewComment("");
      AccessibilityUtils.announceToScreenReader("Comment added successfully", "polite");
    } catch (error) {
      console.error("Failed to add comment:", error);
      AccessibilityUtils.announceToScreenReader("Failed to add comment", "assertive");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle comment editing
  const handleStartEdit = (comment: Comment) => {
    setEditingComment(comment.id);
    setEditingContent(comment.content);
  };

  const handleCancelEdit = () => {
    setEditingComment(null);
    setEditingContent("");
  };

  const handleSaveEdit = async () => {
    if (!editingComment || !editingContent.trim()) return;

    try {
      await onCommentUpdate?.(editingComment, editingContent.trim());
      setEditingComment(null);
      setEditingContent("");
      AccessibilityUtils.announceToScreenReader("Comment updated successfully", "polite");
    } catch (error) {
      console.error("Failed to update comment:", error);
      AccessibilityUtils.announceToScreenReader("Failed to update comment", "assertive");
    }
  };

  // Handle comment deletion
  const handleDeleteComment = async (commentId: string) => {
    if (!confirm(t("confirmDelete"))) return;

    try {
      await onCommentDelete?.(commentId);
      AccessibilityUtils.announceToScreenReader("Comment deleted successfully", "polite");
    } catch (error) {
      console.error("Failed to delete comment:", error);
      AccessibilityUtils.announceToScreenReader("Failed to delete comment", "assertive");
    }
  };

  // Handle reply
  const handleStartReply = (commentId: string) => {
    setReplyingTo(commentId);
    setReplyContent("");
  };

  const handleCancelReply = () => {
    setReplyingTo(null);
    setReplyContent("");
  };

  const handleSubmitReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyingTo || !replyContent.trim()) return;

    try {
      await onReplyAdd?.(replyingTo, {
        content: replyContent.trim(),
        author: {
          id: "current-user",
          name: "Current User",
          avatar: "/avatars/default.jpg",
        },
      });
      setReplyingTo(null);
      setReplyContent("");
      AccessibilityUtils.announceToScreenReader("Reply added successfully", "polite");
    } catch (error) {
      console.error("Failed to add reply:", error);
      AccessibilityUtils.announceToScreenReader("Failed to add reply", "assertive");
    }
  };

  // Handle like/dislike
  const handleLike = async (commentId: string) => {
    try {
      await onCommentLike?.(commentId);
    } catch (error) {
      console.error("Failed to like comment:", error);
    }
  };

  const handleDislike = async (commentId: string) => {
    try {
      await onCommentDislike?.(commentId);
    } catch (error) {
      console.error("Failed to dislike comment:", error);
    }
  };

  // Focus management
  useEffect(() => {
    if (editingComment && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [editingComment]);

  useEffect(() => {
    if (replyingTo && replyTextareaRef.current) {
      replyTextareaRef.current.focus();
    }
  }, [replyingTo]);

  return (
    <div className={cn("space-y-6", className)}>
      {/* Comment Form */}
      <form onSubmit={handleSubmitComment} className="space-y-4">
        <AccessibleTextarea
          label={t("addComment")}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={t("writeComment")}
          required
          className="min-h-[100px]"
        />

        <div className="flex justify-end">
          <AccessibleButton
            type="submit"
            disabled={!newComment.trim() || isSubmitting}
            loading={isSubmitting}
            loadingText={t("posting")}
          >
            {t("postComment")}
          </AccessibleButton>
        </div>
      </form>

      {/* Comments Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          {t("comments")} ({comments.length})
        </h3>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-3 py-1 text-sm border border-input rounded-md bg-background"
        >
          <option value="newest">{t("newest")}</option>
          <option value="oldest">{t("oldest")}</option>
          <option value="popular">{t("mostPopular")}</option>
        </select>
      </div>

      {/* Comments List */}
      <div className="space-y-4">
        {sortedComments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            depth={0}
            maxDepth={maxDepth}
            showReplies={showReplies}
            allowReplies={allowReplies}
            allowEditing={allowEditing}
            allowDeleting={allowDeleting}
            onEdit={handleStartEdit}
            onDelete={handleDeleteComment}
            onReply={handleStartReply}
            onLike={handleLike}
            onDislike={handleDislike}
            isEditing={editingComment === comment.id}
            editingContent={editingContent}
            onEditingContentChange={setEditingContent}
            onSaveEdit={handleSaveEdit}
            onCancelEdit={handleCancelEdit}
            isReplying={replyingTo === comment.id}
            replyContent={replyContent}
            onReplyContentChange={setReplyContent}
            onSubmitReply={handleSubmitReply}
            onCancelReply={handleCancelReply}
            textareaRef={textareaRef}
            replyTextareaRef={replyTextareaRef}
          />
        ))}
      </div>

      {comments.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <p>{t("noComments")}</p>
          <p className="text-sm">{t("beFirstToComment")}</p>
        </div>
      )}
    </div>
  );
}

// Individual Comment Component
interface CommentItemProps {
  comment: Comment;
  depth: number;
  maxDepth: number;
  showReplies: boolean;
  allowReplies: boolean;
  allowEditing: boolean;
  allowDeleting: boolean;
  onEdit: (comment: Comment) => void;
  onDelete: (commentId: string) => void;
  onReply: (commentId: string) => void;
  onLike: (commentId: string) => void;
  onDislike: (commentId: string) => void;
  isEditing: boolean;
  editingContent: string;
  onEditingContentChange: (content: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  isReplying: boolean;
  replyContent: string;
  onReplyContentChange: (content: string) => void;
  onSubmitReply: (e: React.FormEvent) => void;
  onCancelReply: () => void;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  replyTextareaRef: React.RefObject<HTMLTextAreaElement>;
}

function CommentItem({
  comment,
  depth,
  maxDepth,
  showReplies,
  allowReplies,
  allowEditing,
  allowDeleting,
  onEdit,
  onDelete,
  onReply,
  onLike,
  onDislike,
  isEditing,
  editingContent,
  onEditingContentChange,
  onSaveEdit,
  onCancelEdit,
  isReplying,
  replyContent,
  onReplyContentChange,
  onSubmitReply,
  onCancelReply,
  textareaRef,
  replyTextareaRef,
}: CommentItemProps) {
  const t = useTranslations("common");

  if (comment.isDeleted) {
    return (
      <div className={cn("p-4 border border-border rounded-lg bg-muted/50", depth > 0 && "ml-8")}>
        <p className="text-muted-foreground italic">{t("commentDeleted")}</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", depth > 0 && "ml-8")}>
      <div className="p-4 border border-border rounded-lg bg-background">
        {/* Comment Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              {comment.author.avatar ? (
                <img
                  src={comment.author.avatar}
                  alt={comment.author.name}
                  className="w-8 h-8 rounded-full object-cover"
                />
              ) : (
                <span className="text-sm font-medium">
                  {comment.author.name.charAt(0).toUpperCase()}
                </span>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-medium">{comment.author.name}</span>
                {comment.author.role && (
                  <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                    {comment.author.role}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <time dateTime={comment.createdAt}>
                  {new Date(comment.createdAt).toLocaleDateString()}
                </time>
                {comment.isEdited && <span className="text-xs">({t("edited")})</span>}
              </div>
            </div>
          </div>

          {/* Comment Actions */}
          <div className="flex items-center gap-2">
            {allowEditing && (
              <button
                onClick={() => onEdit(comment)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                aria-label={t("editComment")}
              >
                {t("edit")}
              </button>
            )}
            {allowDeleting && (
              <button
                onClick={() => onDelete(comment.id)}
                className="text-xs text-muted-foreground hover:text-destructive transition-colors"
                aria-label={t("deleteComment")}
              >
                {t("delete")}
              </button>
            )}
          </div>
        </div>

        {/* Comment Content */}
        {isEditing ? (
          <div className="space-y-3">
            <textarea
              ref={textareaRef}
              value={editingContent}
              onChange={(e) => onEditingContentChange(e.target.value)}
              className="w-full p-3 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <AccessibleButton variant="outline" size="sm" onClick={onCancelEdit}>
                {t("cancel")}
              </AccessibleButton>
              <AccessibleButton size="sm" onClick={onSaveEdit} disabled={!editingContent.trim()}>
                {t("save")}
              </AccessibleButton>
            </div>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap">{comment.content}</p>
          </div>
        )}

        {/* Comment Actions */}
        {!isEditing && (
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
            <div className="flex items-center gap-4">
              <button
                onClick={() => onLike(comment.id)}
                className={cn(
                  "flex items-center gap-1 text-sm transition-colors",
                  comment.isLiked ? "text-primary" : "text-muted-foreground hover:text-foreground",
                )}
                aria-label={t("likeComment")}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                    clipRule="evenodd"
                  />
                </svg>
                {comment.likes}
              </button>

              <button
                onClick={() => onDislike(comment.id)}
                className={cn(
                  "flex items-center gap-1 text-sm transition-colors",
                  comment.isDisliked
                    ? "text-destructive"
                    : "text-muted-foreground hover:text-foreground",
                )}
                aria-label={t("dislikeComment")}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M3.172 14.828a4 4 0 015.656 0L10 13.657l1.172 1.171a4 4 0 105.656-5.656L10 2.343l-6.828 6.829a4 4 0 000 5.656z"
                    clipRule="evenodd"
                  />
                </svg>
                {comment.dislikes}
              </button>
            </div>

            {allowReplies && depth < maxDepth && (
              <button
                onClick={() => onReply(comment.id)}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {t("reply")}
              </button>
            )}
          </div>
        )}

        {/* Reply Form */}
        {isReplying && (
          <form onSubmit={onSubmitReply} className="mt-4 space-y-3">
            <textarea
              ref={replyTextareaRef}
              value={replyContent}
              onChange={(e) => onReplyContentChange(e.target.value)}
              placeholder={t("writeReply")}
              className="w-full p-3 border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
              rows={3}
            />
            <div className="flex justify-end gap-2">
              <AccessibleButton variant="outline" size="sm" onClick={onCancelReply}>
                {t("cancel")}
              </AccessibleButton>
              <AccessibleButton size="sm" type="submit" disabled={!replyContent.trim()}>
                {t("postReply")}
              </AccessibleButton>
            </div>
          </form>
        )}
      </div>

      {/* Replies */}
      {showReplies && comment.replies.length > 0 && (
        <div className="space-y-4">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              depth={depth + 1}
              maxDepth={maxDepth}
              showReplies={showReplies}
              allowReplies={allowReplies}
              allowEditing={allowEditing}
              allowDeleting={allowDeleting}
              onEdit={onEdit}
              onDelete={onDelete}
              onReply={onReply}
              onLike={onLike}
              onDislike={onDislike}
              isEditing={false}
              editingContent=""
              onEditingContentChange={() => {}}
              onSaveEdit={() => {}}
              onCancelEdit={() => {}}
              isReplying={false}
              replyContent=""
              onReplyContentChange={() => {}}
              onSubmitReply={() => {}}
              onCancelReply={() => {}}
              textareaRef={textareaRef}
              replyTextareaRef={replyTextareaRef}
            />
          ))}
        </div>
      )}
    </div>
  );
}
