import { useAtlasStore } from '../state/store'

const MIN_CHAPTER = 1
const MAX_CHAPTER = 28 // Atos tem 28 capítulos

export default function ChapterTimeline() {
  const chapterRange = useAtlasStore((s) => s.chapterRange)
  const setChapterRange = useAtlasStore((s) => s.setChapterRange)

  const from = chapterRange?.from ?? MIN_CHAPTER
  const to = chapterRange?.to ?? MAX_CHAPTER

  const handleFromChange = (value: number) => {
    setChapterRange({ from: Math.min(value, to), to })
  }

  const handleToChange = (value: number) => {
    setChapterRange({ from, to: Math.max(value, from) })
  }

  const handleReset = () => setChapterRange(null)

  return (
    <div className="chapter-timeline">
      <div className="chapter-range-inputs">
        <label>
          Capítulo
          <input
            type="number"
            min={MIN_CHAPTER}
            max={MAX_CHAPTER}
            value={from}
            onChange={(e) => handleFromChange(Number(e.target.value))}
          />
        </label>
        <span className="chapter-range-inputs__sep">até</span>
        <label>
          Capítulo
          <input
            type="number"
            min={MIN_CHAPTER}
            max={MAX_CHAPTER}
            value={to}
            onChange={(e) => handleToChange(Number(e.target.value))}
          />
        </label>
      </div>
      {chapterRange !== null && (
        <button type="button" onClick={handleReset}>
          Limpar filtro
        </button>
      )}
    </div>
  )
}
