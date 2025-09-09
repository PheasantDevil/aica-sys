import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';
import { getWelcomeEmailTemplate, getNewsletterEmailTemplate, getSubscriptionConfirmationEmailTemplate, getPasswordResetEmailTemplate } from '@/lib/email-templates';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: NextRequest) {
  try {
    const { type, data } = await request.json();

    if (!type || !data) {
      return NextResponse.json(
        { error: 'Type and data are required' },
        { status: 400 }
      );
    }

    let emailTemplate;
    let recipientEmail;
    let recipientName;

    switch (type) {
      case 'welcome':
        recipientEmail = data.email;
        recipientName = data.name;
        emailTemplate = getWelcomeEmailTemplate(recipientName);
        break;

      case 'newsletter':
        recipientEmail = data.email;
        emailTemplate = getNewsletterEmailTemplate(data.newsletter);
        break;

      case 'subscription_confirmation':
        recipientEmail = data.email;
        emailTemplate = getSubscriptionConfirmationEmailTemplate(data.plan, data.amount);
        break;

      case 'password_reset':
        recipientEmail = data.email;
        emailTemplate = getPasswordResetEmailTemplate(data.resetLink);
        break;

      default:
        return NextResponse.json(
          { error: 'Invalid email type' },
          { status: 400 }
        );
    }

    const result = await resend.emails.send({
      from: 'AICA-SyS <noreply@aica-sys.com>',
      to: [recipientEmail],
      subject: emailTemplate.subject,
      html: emailTemplate.html,
      text: emailTemplate.text,
    });

    return NextResponse.json({
      success: true,
      messageId: result.data?.id,
    });

  } catch (error) {
    console.error('Email sending error:', error);
    return NextResponse.json(
      { error: 'Failed to send email' },
      { status: 500 }
    );
  }
}
