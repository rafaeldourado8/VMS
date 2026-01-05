// Value Object: Point
export class Point {
  constructor(
    public readonly x: number,
    public readonly y: number
  ) {
    if (x < 0 || y < 0) {
      throw new Error('Coordinates must be positive');
    }
  }

  distanceTo(other: Point): number {
    return Math.sqrt(
      Math.pow(this.x - other.x, 2) + Math.pow(this.y - other.y, 2)
    );
  }

  toArray(): [number, number] {
    return [this.x, this.y];
  }

  static fromArray([x, y]: [number, number]): Point {
    return new Point(x, y);
  }
}
