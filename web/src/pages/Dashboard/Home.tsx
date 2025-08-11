import TopPosts from "../../components/dashboard/TopPosts";
import StatisticsChart from "../../components/ecommerce/StatisticsChart";
import MonthlyEvaluation from "../../components/ecommerce/MonthlyEvaluation";
import PageMeta from "../../components/common/PageMeta";
import { useState, useEffect } from "react";
import axios from '../../api/axios';
import { useTranslation } from 'react-i18next';

export default function Home() {
  const { t } = useTranslation();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/v1/reports/dashboard/');
        setDashboardData(response.data);
      } catch (err) {
        setError('Failed to fetch dashboard data.');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>{t('dashboard.home.loading')}</div>;
  }

  if (error) {
    return <div>Error: {t('dashboard.home.error')}</div>;
  }

  return (
    <>
      <PageMeta
        title={t('dashboard.home.title')}
        description={t('dashboard.home.description')}
      />
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12 space-y-6 xl:col-span-7">
          <MonthlyEvaluation data={dashboardData.monthly_evaluation} />          
        </div>

        <div className="col-span-12 xl:col-span-5">
          <TopPosts posts={dashboardData.top_posts} />
        </div>

        <div className="col-span-12">
          <StatisticsChart data={dashboardData.daily_evaluation} />
        </div>
      </div>
    </>
  );
}
