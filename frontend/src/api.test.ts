import { describe, expect, it } from 'vitest'
import { formatTime, smallNumber, validateIntegerString } from './api'

describe('mathematical input validation', () => {
  it('accepts exact integers beyond JS safe integer range', () => {
    expect(validateIntegerString('170141183460469231731687303715884105727')).toBeNull()
  })

  it('accepts spaced decimal numbers without rounding', () => {
    expect(validateIntegerString('17 014_118')).toBeNull()
  })

  it('rejects empty, non-digit, negative and less than 2', () => {
    for (const value of ['', '-5', '1', '0', '3.1', '17x', 'Ⅷ']) {
      expect(validateIntegerString(value)).not.toBeNull()
    }
  })

  it('enforces the same 2048 digit bound as the Python API', () => {
    expect(validateIntegerString('9'.repeat(2048))).toBeNull()
    expect(validateIntegerString('9'.repeat(2049))).not.toBeNull()
  })
})

describe('result presentation', () => {
  it('never truncates short numbers', () => {
    expect(smallNumber('561', 2)).toBe('561')
  })
  it('truncates only UI labels, not API data', () => {
    const number = '12345678901234567890'
    expect(smallNumber(number, 4)).toBe('1234…7890')
    expect(number).toBe('12345678901234567890')
  })
  it('formats measured milliseconds with fixed precision', () => {
    expect(formatTime(1.234567)).toBe('1.2346 ms')
  })
})
