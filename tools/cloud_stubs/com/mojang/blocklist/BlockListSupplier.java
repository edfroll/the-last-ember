package com.mojang.blocklist;
import java.util.function.Predicate;
/** Cloud stub of Mojang's blocklist (not downloadable in the cloud): no service implements it, nothing is blocked. */
public interface BlockListSupplier {
    Predicate<String> createBlockList();
}
