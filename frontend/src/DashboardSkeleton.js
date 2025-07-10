import React from 'react';
import './DashboardSkeleton.css';

function DashboardSkeleton() {
  return (
    <div className="dashboard-skeleton">
      <div className="skeleton-header shimmer"></div>

      <div className="skeleton-main">
        <aside className="skeleton-sidebar shimmer"></aside>

        <section className="skeleton-content">
          <div className="skeleton-cards">
            <div className="skeleton-card shimmer"></div>
            <div className="skeleton-card shimmer"></div>
            <div className="skeleton-card shimmer"></div>
          </div>

          <div className="skeleton-charts">
            <div className="skeleton-chart shimmer"></div>
            <div className="skeleton-chart shimmer"></div>
          </div>

          <div className="skeleton-table shimmer"></div>
        </section>
      </div>
    </div>
  );
}

export default DashboardSkeleton;
