import numpy as np
from functools import lru_cache


def fft_convolve(grid, kernel):
    fa = np.fft.fft2(grid)
    fb = np.fft.fft2(kernel)
    convolved = np.fft.ifft2(fa * fb).real
    return convolved

def make_ring_kernel(ring, grid_shape, dist_type="euclidean"):
    h, w = grid_shape
    y, x = np.ogrid[-h//2:h//2, -w//2:w//2]

    if dist_type == "euclidean":
        dist = np.sqrt(x**2 + y**2)
    elif dist_type == "chebyshev":
        dist = np.maximum(np.abs(x), np.abs(y))
    elif dist_type == "manhattan":
        dist = np.abs(x) + np.abs(y)
    else:
        raise ValueError(f"Unknown distance type: {dist_type}")
    
    kernel = (np.round(dist) == ring).astype(np.float32)
    kernel = np.fft.ifftshift(kernel)
    return kernel

ring_sums = {1: 8, 2: 12, 3: 16, 4: 24, 5: 36, 6: 32, 7: 48, 8: 60}

def check_rings(rings, grid, w, h, alive_threshold=0.99, random_life=False, ring_weights=None, dist_type="euclidean", averages=True):
    if grid is None:
        print("No grid given")
    if rings is None:
        rings = [1, 2, 3, 4, 5, 6, 7]
    if ring_weights is None:
        ring_weights = {ring: 1 for ring in rings}

    alive_mask = (grid >= alive_threshold).astype(np.float32)
    sums = np.zeros((h, w))
    totals = np.zeros((h, w))

    if random_life:
        noise = (np.random.uniform(0.0, 1.0, size=(w, h)) > 0.99)
        alive_mask = np.logical_or(alive_mask.astype(bool), noise).astype(np.float32)

    ring_kernels = {}
    for r in rings:
        if r in ring_kernels:
            kernel = ring_kernels[r]
        else:
            kernel = make_ring_kernel(r, grid.shape, dist_type=dist_type)
            ring_kernels[r] = kernel
        conv = fft_convolve(alive_mask, kernel)
        sums += conv * ring_weights[r]
        totals += kernel.sum()

    if averages:
        return sums / totals
    else:
        return sums, totals

def check_rings_old(rings, grid, w, h, alive_threshold=0.99, ring_weights={1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}, random_life=False):
    if grid is None:
        print("No grid given")
    if rings is None:
        rings = [1, 2, 3, 4, 5, 6, 7]

    alive_mask = (grid >= alive_threshold).astype(np.float32)
    sums = np.zeros((h, w))
    totals = np.zeros((h, w))

    if random_life:
        noise = (np.random.uniform(0.0, 1.0, size=(w, h)) > 0.99)
        alive_mask = np.logical_or(alive_mask.astype(bool), noise).astype(np.float32)

    for ring in rings:
        totals += ring_sums[ring]
        # Ring 1
        if ring == 1:
            up1 = np.roll(alive_mask, 1, axis=0)
            down1 = np.roll(alive_mask, -1, axis=0)
            ring_1_sums = (
                up1 + down1 + 
                np.roll(alive_mask, 1, axis=1) + 
                np.roll(alive_mask, -1, axis=1) +
                np.roll(up1, 1, axis=1) +
                np.roll(up1, -1, axis=1) +
                np.roll(down1, 1, axis=1) +
                np.roll(down1, -1, axis=1)
            )
            sums += ring_1_sums * ring_weights[ring]

        # Ring 2
        elif ring == 2:
            up2 = np.roll(alive_mask, 2, axis=0)
            down2 = np.roll(alive_mask, -2, axis=0)
            right2 = np.roll(alive_mask, -2, axis=1)
            left2 = np.roll(alive_mask, 2, axis=1)
            ring_2_sums = (
                up2 + down2 + right2 + left2 +
                np.roll(up2, 1, axis=1) + np.roll(up2, -1, axis=1) + 
                np.roll(down2, 1, axis=1) + np.roll(down2, -1, axis=1) +
                np.roll(right2, 1, axis=0) + np.roll(right2, -1, axis=0) +
                np.roll(left2, 1, axis=0) + np.roll(left2, -1, axis=0)
            )
            sums += ring_2_sums * ring_weights[ring]

        # Ring 3
        elif ring == 3:
            up3 = np.roll(alive_mask, 3, axis=0)
            down3 = np.roll(alive_mask, -3, axis=0)
            right3 = np.roll(alive_mask, -3, axis=1)
            left3 = np.roll(alive_mask, 3, axis=1)
            up2 = np.roll(alive_mask, 2, axis=0)
            down2 = np.roll(alive_mask, -2, axis=0)
            ring_3_sums = (
                up3 + down3 + right3 + left3 +
                np.roll(up3, 1, axis=1) + np.roll(up3, -1, axis=1) + 
                np.roll(down3, 1, axis=1) + np.roll(down3, -1, axis=1) +
                np.roll(right3, 1, axis=0) + np.roll(right3, -1, axis=0) +
                np.roll(left3, 1, axis=0) + np.roll(left3, -1, axis=0) + 
                np.roll(up2, 2, axis=1) + np.roll(up2, -2, axis=1) + 
                np.roll(down2, 2, axis=1) + np.roll(down2, -2, axis=1)
            )
            sums += ring_3_sums * ring_weights[ring]

        # Ring 4
        elif ring == 4:
            up4 = np.roll(alive_mask, 4, axis=0)
            down4 = np.roll(alive_mask, -4, axis=0)
            right4 = np.roll(alive_mask, -4, axis=1)
            left4 = np.roll(alive_mask, 4, axis=1)
            up3 = np.roll(alive_mask, 3, axis=0)
            down3 = np.roll(alive_mask, -3, axis=0)
            right3 = np.roll(alive_mask, -3, axis=1)
            left3 = np.roll(alive_mask, 3, axis=1)
            ring_4_sums = (
                up4 + down4 + right4 + left4 +
                np.roll(up4, 1, axis=1) + np.roll(up4, -1, axis=1) + 
                np.roll(down4, 1, axis=1) + np.roll(down4, -1, axis=1) +
                np.roll(right4, 1, axis=0) + np.roll(right4, -1, axis=0) +
                np.roll(left4, 1, axis=0) + np.roll(left4, -1, axis=0) + 
                np.roll(up3, 2, axis=1) + np.roll(up3, -2, axis=1) + 
                np.roll(down3, 2, axis=1) + np.roll(down3, -2, axis=1) +
                np.roll(right3, 2, axis=0) + np.roll(right3, -2, axis=0) +
                np.roll(left3, 2, axis=0) + np.roll(left3, -2, axis=0) +
                np.roll(up3, 3, axis=1) + np.roll(up3, -3, axis=1) + 
                np.roll(down3, 3, axis=1) + np.roll(down3, -3, axis=1)
            )
            sums += ring_4_sums * ring_weights[ring]

        # Ring 5
        elif ring == 5:
            up5 = np.roll(alive_mask, 5, axis=0)
            down5 = np.roll(alive_mask, -5, axis=0)
            right5 = np.roll(alive_mask, -5, axis=1)
            left5 = np.roll(alive_mask, 5, axis=1)
            up4 = np.roll(alive_mask, 4, axis=0)
            down4 = np.roll(alive_mask, -4, axis=0)
            right4 = np.roll(alive_mask, -4, axis=1)
            left4 = np.roll(alive_mask, 4, axis=1)
            ring_5_sums =(
                up5 + down5 + right5 + left5 + 
                np.roll(up5, 1, axis=1) + np.roll(up5, -1, axis=1) +
                np.roll(up5, 2, axis=1) + np.roll(up5, -2, axis=1) +
                np.roll(down5, 1, axis=1) + np.roll(down5, -1, axis=1) + 
                np.roll(down5, 2, axis=1) + np.roll(down5, -2, axis=1) +
                np.roll(right5, 1, axis=0) + np.roll(right5, -1, axis=0) + 
                np.roll(right5, 2, axis=0) + np.roll(right5, -2, axis=0) +
                np.roll(left5, 1, axis=0) + np.roll(left5, -1, axis=0) + 
                np.roll(left5, 2, axis=0) + np.roll(left5, -2, axis=0) +
                np.roll(up4, 2, axis=1) + np.roll(up4, -2, axis=1) + 
                np.roll(up4, 3, axis=1) + np.roll(up4, -3, axis=1) +
                np.roll(down4, 2, axis=1) + np.roll(down4, -2, axis=1) + 
                np.roll(down4, 3, axis=1) + np.roll(down4, -3, axis=1) +
                np.roll(right4, 2, axis=0) + np.roll(right4, -2, axis=0) + 
                np.roll(right4, 3, axis=0) + np.roll(right4, -3, axis=0) +
                np.roll(left4, 2, axis=0) + np.roll(left4, -2, axis=0) + 
                np.roll(left4, 3, axis=0) + np.roll(left4, -3, axis=0)
            )
            sums += ring_5_sums * ring_weights[ring]

        # Ring 6
        elif ring == 6:
            up6 = np.roll(alive_mask, 6, axis=0)
            down6 = np.roll(alive_mask, -6, axis=0)
            right6 = np.roll(alive_mask, -6, axis=1)
            left6 = np.roll(alive_mask, 6, axis=1)
            up5 = np.roll(alive_mask, 5, axis=0)
            down5 = np.roll(alive_mask, -5, axis=0)
            right5 = np.roll(alive_mask, -5, axis=1)
            left5 = np.roll(alive_mask, 5, axis=1)
            up4 = np.roll(alive_mask, 4, axis=0)
            down4 = np.roll(alive_mask, -4, axis=0)
            ring_6_sums = (
                up6 + down6 + right6 + left6 +
                np.roll(up6, 1, axis=1) + np.roll(up6, -1, axis=1) + 
                np.roll(up6, 2, axis=1) + np.roll(up6, -2, axis=1) + 
                np.roll(down6, 1, axis=1) + np.roll(down6, -1, axis=1) +
                np.roll(down6, 2, axis=1) + np.roll(down6, -2, axis=1) + 
                np.roll(right6, 1, axis=0) + np.roll(right6, -1, axis=0) +
                np.roll(right6, 2, axis=0) + np.roll(right6, -2, axis=0) +
                np.roll(left6, 1, axis=0) + np.roll(left6, -1, axis=0) + 
                np.roll(left6, 2, axis=0) + np.roll(left6, -2, axis=0) +
                np.roll(up5, 3, axis=1) + np.roll(up5, -3, axis=1) + 
                np.roll(down5, 3, axis=1) + np.roll(down5, -3, axis=1) + 
                np.roll(right5, 3, axis=0) + np.roll(right5, -3, axis=0) + 
                np.roll(left5, 3, axis=0) + np.roll(left5, -3, axis=0) + 
                np.roll(up4, 4, axis=1) + np.roll(up4, -4, axis=1) + 
                np.roll(down4, 4, axis=1) + np.roll(down4, -4, axis=1)
            )
            sums += ring_6_sums * ring_weights[ring]

        # Ring 7
        elif ring == 7:
            up7 = np.roll(alive_mask, 7, axis=0)
            down7 = np.roll(alive_mask, -7, axis=0)
            right7 = np.roll(alive_mask, -7, axis=1)
            left7 = np.roll(alive_mask, 7, axis=1)
            up6 = np.roll(alive_mask, 6, axis=0)
            down6 = np.roll(alive_mask, -6, axis=0)
            up5 = np.roll(alive_mask, 5, axis=0)
            down5 = np.roll(alive_mask, -5, axis=0)
            up4 = np.roll(alive_mask, 4, axis=0)
            down4 = np.roll(alive_mask, -4, axis=0)
            up3 = np.roll(alive_mask, 3, axis=0)
            down3 = np.roll(alive_mask, -3, axis=0)
            ring_7_sums = (
                up7 + down7 + right7 + left7 +
                np.roll(up7, 1, axis=1) + np.roll(up7, -1, axis=1) + 
                np.roll(up7, 2, axis=1) + np.roll(up7, -2, axis=1) +
                np.roll(down7, 1, axis=1) + np.roll(down7, -1, axis=1) +
                np.roll(down7, 2, axis=1) + np.roll(down7, -2, axis=1) +
                np.roll(right7, 1, axis=0) + np.roll(right7, -1, axis=0) + 
                np.roll(right7, 2, axis=0) + np.roll(right7, -2, axis=0) +
                np.roll(left7, 1, axis=0) + np.roll(left7, -1, axis=0) + 
                np.roll(left7, 2, axis=0) + np.roll(left7, -2, axis=0) +
                np.roll(up6, 3, axis=1) + np.roll(up6, -3, axis=1) + 
                np.roll(up6, 4, axis=1) + np.roll(up6, -4, axis=1) +
                np.roll(down6, 3, axis=1) + np.roll(down6, -3, axis=1) +
                np.roll(down6, 4, axis=1) + np.roll(down6, -4, axis=1) +
                np.roll(up5, 4, axis=1) + np.roll(up5, -4, axis=1) + 
                np.roll(up5, 5, axis=1) + np.roll(up5, -5, axis=1) + 
                np.roll(down5, 4, axis=1) + np.roll(down5, -4, axis=1) +
                np.roll(down5, 5, axis=1) + np.roll(down5, -5, axis=1) +
                np.roll(up4, 5, axis=1) + np.roll(up4, -5, axis=1) +
                np.roll(up4, 6, axis=1) + np.roll(up4, -6, axis=1) +
                np.roll(down4, 5, axis=1) + np.roll(down4, -5, axis=1) +
                np.roll(down4, 6, axis=1) + np.roll(down4, -6, axis=1) +
                np.roll(up3, 6, axis=1) + np.roll(up3, -6, axis=1) + 
                np.roll(down3, 6, axis=1) + np.roll(down3, -6, axis=1)
            )
            sums += ring_7_sums * ring_weights[ring]
            
    return sums / totals