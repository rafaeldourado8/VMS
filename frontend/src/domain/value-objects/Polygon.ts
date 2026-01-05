// Value Object: Polygon (ROI)
import { Point } from './Point';

export class Polygon {
  constructor(public readonly points: Point[]) {
    if (points.length < 3) {
      throw new Error('Polygon must have at least 3 points');
    }
  }

  containsPoint(point: Point): boolean {
    let inside = false;
    const n = this.points.length;

    let p1 = this.points[0];
    for (let i = 1; i <= n; i++) {
      const p2 = this.points[i % n];
      if (point.y > Math.min(p1.y, p2.y)) {
        if (point.y <= Math.max(p1.y, p2.y)) {
          if (point.x <= Math.max(p1.x, p2.x)) {
            if (p1.y !== p2.y) {
              const xinters = (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x;
              if (p1.x === p2.x || point.x <= xinters) {
                inside = !inside;
              }
            }
          }
        }
      }
      p1 = p2;
    }

    return inside;
  }

  toArray(): [number, number][] {
    return this.points.map(p => p.toArray());
  }

  static fromArray(points: [number, number][]): Polygon {
    return new Polygon(points.map(([x, y]) => new Point(x, y)));
  }
}
