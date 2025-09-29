import AuditDashboard from '@/components/audit/audit-dashboard';
import { Suspense } from 'react';

export const metadata = {
  title: 'Audit Dashboard - AICA-SyS',
  description: 'Security audit and compliance monitoring for AICA-SyS.',
};

const AuditPage = () => {
  return (
    <Suspense fallback={<div>Loading audit page...</div>}>
      <AuditDashboard />
    </Suspense>
  );
};

export default AuditPage;
