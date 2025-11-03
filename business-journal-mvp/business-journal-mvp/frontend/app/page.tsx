import { DashboardSummary } from '@/components/dashboard-summary'
import { JournalForm } from '@/components/journal-form'
import { ContentKanban } from '@/components/content-kanban'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">사업일기</h1>
          <p className="text-gray-600 mt-2">
            투명한 실행-로그-학습 SaaS
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 대시보드 요약 */}
          <div className="lg:col-span-2">
            <DashboardSummary />
          </div>

          {/* 오늘의 추천 */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">오늘의 셀링 포인트</h2>
              <ul className="space-y-2">
                <li className="text-sm text-gray-700">• 조용한 작업 공간</li>
                <li className="text-sm text-gray-700">• 넓은 테이블과 콘센트</li>
                <li className="text-sm text-gray-700">• 비주얼 좋은 브런치</li>
              </ul>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">저경쟁 키워드</h2>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  동네 카페
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  작업 카페
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  조용한 브런치
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 일기 작성 섹션 */}
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">사업 일기 작성</h2>
          <JournalForm />
        </div>

        {/* 콘텐츠 관리 섹션 */}
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">콘텐츠 월관리</h2>
          <ContentKanban />
        </div>
      </div>
    </main>
  )
}
